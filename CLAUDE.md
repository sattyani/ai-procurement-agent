# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Update This File
After every successful change (when the user confirms the changes are good), update this CLAUDE.md file to reflect any new architectural patterns, dependencies, commands, or project structure changes that future Claude instances should know about.

## Project Overview

This is a complete AI procurement agent built with Python that processes vendor PDF proposals and extracts key information for procurement teams. The project uses true AI-powered extraction (GPT-4o) combined with semantic search capabilities via Superlinked for intelligent proposal comparison.

## Project Structure

- `main.py`: Main application orchestrator with Superlinked integration
- `pdf_processor.py`: AI-powered PDF extraction engine using GPT-4o
- `sample_data.py`: Testing framework with mock proposal data
- `pyproject.toml`: Python project configuration and dependencies
- `data/proposals/`: Directory for PDF vendor proposals
- `outputs/`: Directory for extracted JSON results
- `.env`: Environment variables (gitignored)
- `README.md`: Comprehensive project documentation

## Development Commands

### Running the Application
```bash
# Production mode (process PDFs from data/proposals/)
python main.py

# Test mode (use sample data)
# Edit main.py to set TEST_MODE = "sample"
python main.py
```

### Python Environment
- Requires Python >=3.13
- Uses pyproject.toml for dependency management
- Key Dependencies:
  - `langchain` (0.3.26+): Document processing and LLM integration
  - `langchain-community`: Document loaders (PyPDFLoader)
  - `langchain-openai`: OpenAI integration
  - `superlinked` (29.6.4): Vector database and semantic search
  - `openai`: GPT-4o model access
  - `pypdf`: PDF document processing
  - `python-dotenv`: Environment variable management
  - `pydantic`: Data validation and structured output
  - `pandas`: Data manipulation

### Environment Setup
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

The project uses `python-dotenv` to automatically load environment variables from the `.env` file.

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

### CRITICAL: This is a TRUE AI Agent
This project uses **AI-powered extraction**, not regex patterns or keyword matching. The core principle is that GPT-4o reads and comprehends proposal content like a human procurement analyst would.

### Core Components:

1. **AI-Powered PDF Processing** (`pdf_processor.py`):
   - Uses `ChatOpenAI` with GPT-4o model (temperature=0 for consistency)
   - Structured prompting as a "procurement analyst expert"
   - Pydantic models for type-safe output validation
   - Processes entire document content for context-aware extraction

2. **Superlinked Vector Database Integration**:
   - `VendorProposal` schema with structured fields
   - `TextSimilaritySpace` for scope and risk content
   - `NumberSpace` for pricing information
   - Combined index for multi-faceted search
   - Semantic search capabilities for proposal comparison

3. **Modular Testing Framework** (`sample_data.py`):
   - 5 comprehensive test proposals with varied content
   - 5 search scenarios covering different use cases
   - Validates both extraction accuracy and semantic search

4. **Dual Operating Modes**:
   - `TEST_MODE = "sample"`: Uses sample data for development/testing
   - `TEST_MODE = "pdf"`: Processes real PDFs from data folder

### Key Architecture Patterns:

- **No Regex/Keywords**: Completely AI-driven content understanding
- **Structured Output**: Pydantic models ensure data consistency
- **Environment Variables**: Uses `python-dotenv` for configuration
- **Error Handling**: Comprehensive error handling for AI and PDF processing
- **Modular Design**: Clear separation between testing and production
- **Type Safety**: Full Pydantic validation throughout pipeline

### Data Flow:
1. **PDF Loading**: PyPDFLoader processes PDF documents
2. **Duplicate Check**: Checks if PDF already processed (JSON exists in outputs/)
3. **AI Analysis**: GPT-4o analyzes full document content (skipped if already processed)
4. **Structured Extraction**: Pydantic models validate extracted data
5. **JSON Persistence**: Results saved to outputs/ directory with metadata
6. **Vector Storage**: Superlinked indexes content for semantic search

## Important Implementation Details

### AI Extraction Process
The `pdf_processor.py` uses a sophisticated prompt that instructs GPT-4o to act as a procurement analyst expert. Key aspects:
- Analyzes ENTIRE document content (not just sections)
- Understands that pricing/scope/risks can be scattered throughout
- Provides intelligent risk assessment and timeline breakdown
- Uses structured Pydantic output for validation

### Superlinked Schema
The `VendorProposal` schema includes:
- `id`: Unique identifier
- `vendor_name`: Company name
- `project_name`: Project identifier
- `timestamp`: Processing timestamp
- `price`: Extracted pricing information
- `delivery_timeline`: Project timeline details
- `scope_summary`: Work scope description
- `risks`: Risk assessment and mitigation

### Testing Strategy
Always test with sample data first (`TEST_MODE = "sample"`) before processing real PDFs. The sample data includes diverse scenarios to validate AI extraction quality.

### Smart Caching System
The system automatically skips already processed PDFs to avoid duplicate work and API costs:
- **Detection**: Checks for existing JSON files in `outputs/` directory
- **Naming**: JSON files follow pattern `{pdf_name}_extracted.json`
- **Metadata**: Each JSON includes processing timestamp and source PDF info
- **Loading**: Previously processed data is loaded from JSON instead of re-extraction

### Cache Management
To force reprocessing of specific files:
1. Delete the corresponding JSON file in `outputs/` directory
2. The system will detect missing JSON and reprocess the PDF
3. Alternatively, implement a `force_reprocess` flag if needed

## Common Patterns

### Adding New Extraction Fields
1. Update the Pydantic model in `pdf_processor.py`
2. Modify the AI prompt to include new field extraction
3. Update the Superlinked schema if searchable
4. Add test cases in `sample_data.py`

### Debugging AI Extraction
- Check the full document content being sent to GPT-4o
- Verify Pydantic model validation
- Review AI model temperature settings (should be 0 for consistency)
- Test with sample data to isolate issues

## User Preferences
- **Step-by-step development**: User prefers incremental changes and does not want code written automatically
- **Explicit requests**: Only make changes when explicitly requested
- **Testing first**: Always validate with sample data before processing real PDFs

## Dependencies Management
The project uses `pyproject.toml` for dependency management. Key version constraints:
- LangChain packages must be compatible (0.3.26+)
- Superlinked version 29.6.4 for stability
- OpenAI package for GPT-4o access
- Python-dotenv for environment management

## Error Handling Patterns
- AI extraction errors fall back to "Unable to extract" values
- PDF processing errors are logged and handled gracefully
- Environment variable validation on startup
- Pydantic validation ensures data integrity