# Red Green Machine

An AI-powered Test-Driven Development (TDD) automation tool that implements the classic "Red-Green-Refactor" cycle using multiple AI agents working together.

## What This Repository Does

The Red Green Machine is an intelligent TDD assistant that automates the traditional Test-Driven Development workflow:

1. **🔴 Red Phase**: Analyzes failing tests and understands what needs to be implemented
2. **🟢 Green Phase**: Generates minimal code to make tests pass
3. **🔄 Refactor Phase**: Improves code quality while maintaining test coverage

## Key Features

- **Multi-Agent AI System**: Specialized AI agents handle different aspects of the TDD cycle
- **Real-time Web Interface**: Interactive Gradio-based UI showing the development process
- **Automated Code Generation**: Uses Google Gemini AI to write Python code that satisfies tests
- **Intelligent Test Analysis**: Analyzes pytest output to understand failure root causes
- **Code Refactoring**: Automatically improves code quality with type hints and documentation
- **File Management**: Safely writes generated code to your repository

## Architecture

The system consists of several specialized AI agents:

- **GetRepoAgent**: Scans and reads repository files
- **RunTestsAgent**: Executes test commands and analyzes results  
- **AnalystAgent**: Analyzes test failures and provides implementation guidance
- **CoderAgent**: Generates Python code to make failing tests pass
- **RefactorAgent**: Improves code quality while maintaining functionality
- **WriteFilesAgent**: Safely saves generated code to files
- **DoneAgent**: Signals workflow completion

## Prerequisites

- Python 3.12+
- Google Gemini API key
- UV package manager (recommended) or pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/onycher/red_green_machine.git
cd red_green_machine
```

2. Install dependencies:
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -e .
```

3. Set up your Google Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Usage

1. **Start the Web Interface**:
```bash
python rgm.py
```

2. **Configure Your Repository**: 
   - Update the `repo` configuration in `rgm.py` to point to your test repository
   - Ensure your repository has failing tests that need implementation

3. **Run the TDD Cycle**:
   - Open the Gradio interface in your browser
   - Click "Run" to start the automated TDD process
   - Watch as AI agents analyze tests, generate code, and refactor implementations

## Configuration

Edit the `Repo` configuration in `rgm.py`:

```python
repo = Repo(
    path=Path("path/to/your/project"),     # Your project directory
    includes=[".py"],                       # File extensions to include
    excludes=[".venv", ".python-version"], # Directories to exclude
    test_cmd="uv run pytest",              # Test command to run
)
```

## How It Works

1. **Repository Analysis**: Scans your codebase and identifies Python files
2. **Test Execution**: Runs your test suite to identify failures
3. **Failure Analysis**: AI analyzes pytest output to understand what needs to be implemented
4. **Code Generation**: AI generates minimal code to satisfy failing tests
5. **Validation**: Re-runs tests to ensure the generated code works
6. **Refactoring**: Improves code quality with proper type hints and documentation
7. **Iteration**: Repeats the cycle until all tests pass

## Dependencies

- **google-genai**: Google Gemini AI integration
- **gradio**: Web interface framework
- **ollama**: Alternative AI model support
- **parse**: Text parsing utilities
- **pydantic-ai**: AI framework with logging
- **textual**: Terminal UI components

## Development

The codebase includes development tools:

- **pyright**: Type checking
- **ruff**: Linting and formatting

Run linting:
```bash
ruff check .
ruff format .
```

Run type checking:
```bash
pyright
```

## License

This project is open source. Please check the repository for license details.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.
