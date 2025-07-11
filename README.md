# AI Procurement Agent

An intelligent AI-powered procurement agent that processes vendor PDF proposals and extracts key information for procurement teams. Built with LangChain, Superlinked, and OpenAI GPT-4o for semantic understanding and comparison of vendor proposals.

## 🎯 Project Overview

This agent solves the common procurement challenge where companies receive multiple vendor proposals in PDF format and need to quickly extract and compare key information like pricing, scope, timeline, and risks. Instead of manual review, this AI agent intelligently processes all proposals and enables semantic search for efficient comparison.

## 🚀 Key Features

- **AI-Powered Extraction**: Uses GPT-4o to intelligently analyze proposal content (not regex patterns)
- **Semantic Search**: Superlinked vector database enables meaning-based search across proposals
- **Structured Output**: Extracts pricing, timeline, scope, and risk information into structured format
- **Batch Processing**: Processes multiple PDFs from a folder automatically
- **Smart Caching**: Skips already processed files to avoid duplicate work and API costs
- **Modular Architecture**: Clean separation between testing and production modes
- **Type Safety**: Pydantic models ensure data validation and consistency

## 🏗️ Architecture

### Core Components

1. **PDF Processor** (`pdf_processor.py`): AI-powered extraction engine
2. **Main Pipeline** (`main.py`): Orchestrates processing and search
3. **Sample Data** (`sample_data.py`): Testing framework with mock data
4. **Superlinked Integration**: Vector search and semantic comparison

### Tech Stack

- **LangChain** (0.3.26+): Document processing and LLM integration
- **Superlinked** (29.6.4): Vector database and semantic search
- **OpenAI GPT-4o**: AI model for intelligent content extraction
- **PyPDF**: PDF document processing
- **Pydantic**: Data validation and structured output
- **python-dotenv**: Environment variable management

## 📋 Extracted Information

The agent extracts the following key information from each proposal:

- **Vendor Name**: Company submitting the proposal
- **Project Name**: Specific project being proposed
- **Pricing**: Cost information (can be scattered throughout document)
- **Delivery Timeline**: Project duration and milestones
- **Scope Summary**: What work will be performed
- **Risk Assessment**: Potential risks and mitigation strategies

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.13+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-procurements-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

## 🚀 Usage

### Processing PDF Proposals

1. **Add PDF proposals** to the `data/proposals/` directory
2. **Run the agent**:
   ```bash
   python main.py
   ```

### Testing with Sample Data

For development and testing:
```bash
# Edit main.py to set TEST_MODE = "sample"
python main.py
```

### Search and Query

The agent provides interactive search capabilities:
- Semantic search across all proposals
- Price range filtering
- Timeline-based queries
- Risk assessment comparisons

## 📁 Project Structure

```
ai-procurements-agent/
├── main.py                    # Main application entry point
├── pdf_processor.py           # AI-powered PDF extraction
├── sample_data.py            # Testing framework
├── data/
│   └── proposals/            # PDF proposals folder
├── outputs/                  # Extracted JSON results
├── pyproject.toml           # Dependencies and project config
├── .env                     # Environment variables
└── README.md               # This file
```

## 🔍 Example Workflow

1. **RFP Issued**: Company issues Request for Proposal
2. **Vendors Respond**: Multiple vendors submit PDF proposals
3. **Copy PDFs**: Procurement team copies PDFs to `data/proposals/`
4. **Run Agent**: AI agent processes all proposals automatically
5. **Compare Results**: Use semantic search to compare vendors

## 🧪 Testing

The project includes comprehensive testing with sample data:
- 5 test proposals with varied content
- 5 search scenarios covering different use cases
- Semantic search validation
- AI extraction accuracy testing

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Mode Configuration

In `main.py`:
- `TEST_MODE = "sample"`: Use sample data for testing
- `TEST_MODE = "pdf"`: Process real PDFs from data folder

## 🤝 Contributing

This project follows a step-by-step development approach. When contributing:

1. Focus on one feature at a time
2. Test thoroughly with sample data first
3. Ensure AI extraction quality over speed
4. Maintain modular architecture

## 📄 License

See LICENSE file for details.

## 🆘 Support

For issues or questions about the AI procurement agent, please check the existing documentation or create an issue in the repository.