from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from subprocess import run
from typing import Any, Generator, Optional, Type

import ollama
from google import genai
from google.genai import types
import prompts
from data import EndStatus, File, Repo, RepoContent, Stage
from utilities import format_repo_content
import time
import os
import json


def generate(model, prompt, system):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for i in range(3):
        try:
            return client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=8192,
                    temperature=0.9,
                ),
            )
        except:
            time.sleep(60)
            continue
    raise ConnectionError()


def generate_code(model, prompt, system):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for i in range(3):
        try:
            return client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=8192,
                    temperature=0.9,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "files": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string"},
                                        "sourcecode": {"type": "string"},
                                    },
                                    "required": ["path", "sourcecode"],
                                },
                            }
                        },
                        "required": ["files"],
                    },
                ),
            )
        except:
            time.sleep(60)
            continue
    raise ConnectionError()


class Agent:
    def __init__(self, ctx):
        self.ctx = ctx

    @abstractmethod
    def __call__(self, input: Any) -> Generator[tuple[Optional[Type[Agent]], Any, Any]]:
        pass


class AgentGraph:
    def __init__(self, nodes: list[Type[Agent]], model: str, repo: Repo):
        self.nodes = {c: c(self) for c in nodes}
        self.model = model
        self.repo = repo
        self.repo_content = RepoContent(files=[])

    def node(self, node_class: Type[Agent]) -> Agent:
        return self.nodes[node_class]

    def __call__(self, agent=Agent) -> Agent:
        return self.node(agent)


class DoneAgent(Agent):
    def __call__(self, input: EndStatus):
        yield None, None, input


class AnalystAgent(Agent):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.tries = 0
        self.max_tries = 3

    def __call__(self, input):
        if self.tries >= self.max_tries:
            yield self.ctx.node(DoneAgent), EndStatus(), "Implementation failed"
            return
        self.tries += 1
        prompt = f"""{format_repo_content(self.ctx.repo_content)}
Test results:
{input}"""
        for i in range(3):
            try:
                response = generate(
                    self.ctx.model,
                    prompt,
                    system=prompts.orchestrator_system_prompt,
                )
                content = []
                for part in response:
                    content.append(part.text)
                    yield None, None, part.text
                break
            except:
                time.sleep(60)
        yield self.ctx.node(CoderAgent), "".join(content), None


class CoderAgent(Agent):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.tries = 0
        self.max_tries = 3

    def __call__(self, input):
        if self.tries >= self.max_tries:
            yield self.ctx.node(DoneAgent), EndStatus(), "Implementation failed"
            return
        self.tries += 1
        prompt = f"""This is the current state of the repository:
{format_repo_content(self.ctx.repo_content)}
{input}"""
        for i in range(3):
            try:
                response = generate_code(
                    self.ctx.model,
                    prompt,
                    system=prompts.coder_system_prompt,
                )
                content = []
                for part in response:
                    content.append(part.text)
                    yield None, None, part.text
                break
            except:
                time.sleep(60)

        content = "".join(content)
        content_json = json.loads(content)
        data = {file["path"]: file["sourcecode"] for file in content_json["files"]}

        yield (
            self.ctx.node(WriteFilesAgent),
            (Stage.implement, data),
            content,
        )


class RefactorAgent(Agent):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.tries = 0
        self.max_tries = 3

    def __call__(self, input):
        if self.tries >= self.max_tries:
            yield self.ctx.node(DoneAgent), EndStatus(), "Implementation failed"
            return
        self.tries += 1
        prompt = f"""This is the current state of the repository:
{format_repo_content(self.ctx.repo_content)}
{input}"""
        for i in range(3):
            try:
                response = generate_code(
                    self.ctx.model,
                    prompt,
                    system=prompts.refactor_system_prompt,
                )
                content = []
                for part in response:
                    content.append(part.text)
                    yield None, None, part.text
                break
            except:
                time.sleep(60)

        content = "".join(content)
        content_json = json.loads(content)
        data = {file["path"]: file["sourcecode"] for file in content_json["files"]}

        yield (self.ctx.node(WriteFilesAgent), (Stage.refactor, data), content)


class WriteFilesAgent(Agent):
    def __call__(self, input):
        stage, data = input
        for path, content in data.items():
            write_path = Path(path)
            if "test" in write_path.parts or "tests" in write_path.parts:
                continue
            if write_path.is_absolute():
                if not write_path.is_relative_to(self.ctx.repo.path):
                    yield self.ctx.node(RunTestsAgent), Stage.init, None
            else:
                write_path = self.ctx.repo.path / write_path
            write_path.parent.mkdir(parents=True, exist_ok=True)
            with write_path.open("w") as f:
                f.write(content)
            for file in self.ctx.repo_content.files:
                if file.path == write_path:
                    file.content = content
                else:
                    self.ctx.repo_content.files.append(
                        File(path=write_path, content=content)
                    )
        yield self.ctx.node(RunTestsAgent), stage, "Files saved"


class RunTestsAgent(Agent):
    def __call__(self, input: Stage):
        out = run(
            self.ctx.repo.test_cmd, capture_output=True, cwd=self.ctx.repo.path
        ).stdout.decode()
        fails = "FAILURES" in out or "ERRORS" in out
        if input == Stage.init:
            if fails:
                yield self.ctx.node(AnalystAgent), out, f"Test results:\n```{out}```\n"
            yield (
                self.ctx.node(DoneAgent),
                EndStatus(tests_passed=True, implemented_file=False, failed=False),
                f"Test results:\n```{out}```\n",
            )
        if input == Stage.implement:
            if fails:
                yield self.ctx.node(AnalystAgent), out, f"Test results:\n```{out}```\n"
            yield self.ctx.node(RefactorAgent), None, f"Test results:\n```{out}```\n"

        if input == Stage.refactor:
            if fails:
                yield (
                    self.ctx.node(RefactorAgent),
                    False,
                    f"Test results:\n```{out}```\n",
                )
            yield (
                self.ctx.node(DoneAgent),
                EndStatus(tests_passed=True, implemented_file=True, failed=False),
                f"Test results:\n```{out}```\n",
            )


class GetRepoAgent(Agent):
    def __call__(self, input=None):
        for dirpath, _, filenames in self.ctx.repo.path.walk():
            for filename in filenames:
                fn = dirpath / filename
                if any(
                    include in filename for include in self.ctx.repo.includes
                ) and all(
                    exclude not in fn.parts for exclude in self.ctx.repo.excludes
                ):
                    with fn.open() as f:
                        self.ctx.repo_content.files.append(
                            File(Path(dirpath) / filename, f.read())
                        )
        yield self.ctx.node(RunTestsAgent), Stage.init, "Repo content collected"
