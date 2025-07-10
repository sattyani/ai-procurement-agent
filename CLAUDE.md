# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Update This File
After every successful change (when the user confirms the changes are good), update this CLAUDE.md file to reflect any new architectural patterns, dependencies, commands, or project structure changes that future Claude instances should know about.

## Project Overview

This is an AI procurements agent built with Python. The project is in its initial stages with a minimal setup containing a basic Python entry point.

## Project Structure

- `main.py`: Entry point for the application
- `pyproject.toml`: Python project configuration and dependencies
- `README.md`: Project documentation (currently empty)

## Development Commands

### Running the Application
```bash
python main.py
```

### Python Environment
- Requires Python >=3.13
- Uses pyproject.toml for dependency management
- Currently has no external dependencies

## GitHub Actions Integration

### Claude Code PR Reviews
This repository is configured with GitHub Actions for automated Claude Code PR reviews:
- Triggered by mentioning `@claude` in PR comments or issues
- Requires GitHub App and Anthropic API key configuration
- Workflow file: `.github/workflows/claude-code.yml`

Required repository secrets:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `APP_ID`: GitHub App ID  
- `APP_PRIVATE_KEY`: Private key for the GitHub App

## Architecture Notes

The project is currently a simple Python application with a single entry point. As this is an AI procurements agent, it will likely expand to include:
- AI/ML model integration
- Procurement data processing
- API endpoints or CLI interfaces
- Database interactions for procurement data

The current structure suggests this is a foundational setup that will grow as the procurement agent functionality is developed.