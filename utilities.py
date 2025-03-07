from data import RepoContent


def format_repo_content(repo_content: RepoContent) -> str:  # noqa: D103
    ff = []
    for file in repo_content.files:
        ff.append(
            f"""# {file.path}
```python
{file.content}```"""
        )
    return "\n".join(ff)
