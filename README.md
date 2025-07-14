# Red Green Machine

A Test-Driven Development (TDD) automation tool powered by AI that helps implement code to pass failing tests.

## Overview

Red Green Machine is an AI-powered tool that follows the red-green-refactor cycle of TDD:
- **Red**: Analyzes failing tests 
- **Green**: Generates code to make tests pass
- **Refactor**: Improves code quality while maintaining functionality

## Features

- **Multi-Agent Architecture**: Different AI agents handle analysis, coding, and refactoring
- **Gradio Web Interface**: User-friendly web UI for interaction
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Configurable Repository Path**: Set via environment variable or use current directory

## Usage

### Configuration

Set the repository path (optional):
```bash
export RGM_REPO_PATH=/path/to/your/project
```

If not set, the current directory (`.`) will be used.

### Running the Application

```bash
python rgm.py
```

This will launch the Gradio interface where you can interact with the Red Green Machine.

## Requirements

- Python 3.12+
- Dependencies listed in `pyproject.toml`
- GEMINI_API_KEY environment variable for AI functionality

## Project Structure

- `rgm.py` - Main Gradio interface
- `agents.py` - Core agent system for TDD workflow
- `data.py` - Data models for repositories and files
- `prompts.py` - AI system prompts for different agents
- `utilities.py` - Helper functions
