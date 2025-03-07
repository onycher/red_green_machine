from pathlib import Path
import json
from agents import (
    AgentGraph,
    AnalystAgent,
    CoderAgent,
    DoneAgent,
    GetRepoAgent,
    RefactorAgent,
    RunTestsAgent,
    WriteFilesAgent,
)

import gradio as gr

from data import Repo


with gr.Blocks() as rgm:
    chatbot = gr.Chatbot(
        type="messages",
        label="Red Green Machine",
        group_consecutive_messages=False,
        resizeable=True,
    )
    run = gr.Button("Run")

    def run_rgm(history, run):
        repo = Repo(
            path=Path("C:/test"),
            includes=[".py"],
            excludes=[".venv", ".python-version"],
            test_cmd="uv run pytest",
        )
        graph = AgentGraph(
            [
                GetRepoAgent,
                RunTestsAgent,
                AnalystAgent,
                CoderAgent,
                RefactorAgent,
                WriteFilesAgent,
                DoneAgent,
            ],
            "gemini-2.0-flash-exp",
            repo,
        )
        agent = graph(GetRepoAgent)
        input = None
        output = None
        while True:
            if agent is None:
                break
            node = agent(input)
            has_msg = False
            if isinstance(agent, AnalystAgent):
                history.append({"role": "assistant", "content": ""})
                has_msg = True
            elif isinstance(agent, (CoderAgent, RefactorAgent)):
                history.append({"role": "user", "content": ""})
                has_msg = True
            else:
                history.append({"role": "assistant", "content": ""})

            for part in node:
                agent, input, output = part

                if agent is not None:
                    if not has_msg and output is not None:
                        history[-1]["content"] = output
                        yield history, run
                    elif isinstance(agent, WriteFilesAgent):
                        content_json = json.loads(output)
                        data = {
                            file["path"]: file["sourcecode"]
                            for file in content_json["files"]
                        }
                        out = []
                        for k, v in data.items():
                            out.append(f"# {k}\n")
                            out.append(f"```python\n{v}\n```\n")

                        history[-1]["content"] = "".join(out)
                        yield history, run
                    break
                else:
                    if has_msg and output is not None:
                        history[-1]["content"] += output
                        yield history, run

    run.click(run_rgm, [chatbot, run], [chatbot, run])

if __name__ == "__main__":
    rgm.launch()
