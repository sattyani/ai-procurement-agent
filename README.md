# AI Procurement Agent - Capstone Project

> **Enterprise-Grade AI-Powered Procurement Analysis System with Interactive Web Interface**

An intelligent AI procurement agent that automates the entire procurement evaluation process - from RFP analysis to vendor scoring and final recommendations. Features both command-line processing and an intuitive **Streamlit web interface** for interactive procurement analysis.

## 🎯 Project Vision & Purpose

This capstone project demonstrates how **AI can revolutionize procurement operations** by:

- **Eliminating Manual Analysis**: Automatically processes RFP documents and vendor proposals
- **Interactive Web Interface**: User-friendly Streamlit app for easy procurement analysis
- **Ensuring Objective Evaluation**: AI-driven scoring removes human bias and inconsistency  
- **Accelerating Decision-Making**: Reduces weeks of manual work to minutes of AI processing
- **Providing Audit Trail**: Complete justification and reasoning for every recommendation
- **Scaling Procurement Operations**: Handle multiple RFPs and dozens of vendors simultaneously

**Real-World Impact**: Designed for government agencies, enterprises, and organizations managing complex procurement processes.

## 🌐 Interactive Web Interface

### **Streamlit Application**
Launch the interactive web interface for easy procurement analysis:

```bash
# Start the web application
uv run streamlit run streamlit_app.py
```

**Features**:
- **📁 File Management**: Automatic scanning of proposal PDFs
- **🔍 One-Click Analysis**: Simple "Analyze" button to process all vendors
- **📊 Real-time Results**: Live progress indicators and instant results
- **📈 Comprehensive Display**: 
  - Vendor ranking table with all criteria scores
  - Detailed proposal content for each vendor
  - Executive insights and recommendations
- **📱 Responsive Design**: Full-width layout optimized for modern browsers

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🏢 AI Procurement Agent                                     │
│                                                             │
│ 📂 Folder                                                   │
│ [data/proposals/              ] [Analyze]                   │
│                                                             │
│ 📄 Files                                                    │
│ 1. acme_corp_proposal.pdf                                  │
│ 2. Nexora_Proposal.pdf                                     │
│ 3. Stratiform_Proposal.pdf                                 │
│ 4. TechNova_Proposal.pdf                                   │
│                                                             │
│ 🏆 VENDOR RANKING                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Rank │ Vendor │ Technical │ Cost │ Timeline │ Total     │ │
│ │  1   │ Tech...│    9.0    │ 8.0  │   8.0    │  8.40    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ 📋 DETAILED VENDOR ANALYSIS                                 │
│ ▼ TechNova FZ-LLC (Click to expand)                        │
│   Executive Summary, Technical Approach, Timeline...       │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ System Architecture & Approach

### **Dual Interface Design**
- **🌐 Web Interface**: Streamlit app for interactive analysis
- **⚡ Command Line**: Full pipeline for batch processing
- **📊 Unified Results**: Consistent output across both interfaces

### **Smart Evaluation Modes**
- **🧠 Full AI Evaluation**: Complete GPT-4o analysis with detailed justification
- **⚡ Heuristic Evaluation**: Fast, rule-based scoring for quick analysis
- **🎯 Adaptive Processing**: Choose evaluation depth based on requirements

### **Technical Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RFP Analysis  │    │ Vendor Analysis │    │ AI Evaluation   │
│   (Shape 1)     │───▶│   (Shape 2)     │───▶│   (Shape 3)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
 📄 RFP Schema          📊 Proposal Data      🏆 Final Rankings
 📋 Requirements        💰 Budget/Timeline     📈 Analytics
 ⚖️ Criteria Weights   ✅ Compliance Check    🎯 Recommendations
           │                                            │
           └────────────── 🌐 Streamlit UI ─────────────┘
```

## 🚀 Complete Workflow

### **🌐 Web Interface Workflow**
1. **Launch Application**: `uv run streamlit run streamlit_app.py`
2. **Automatic Scanning**: App scans `data/proposals/` folder
3. **One-Click Analysis**: Click "Analyze" button to process all vendors
4. **Real-time Progress**: Watch analysis progress with status indicators
5. **Interactive Results**: Explore rankings, scores, and detailed vendor information

### **📖 Shape 1: RFP Analysis** (Command Line)
**Purpose**: Extract structured requirements from RFP documents

**Process**:
1. **PDF Loading**: Parse RFP document using LangChain PyPDFLoader
2. **AI Extraction**: GPT-4o extracts project details, scope, evaluation criteria
3. **Schema Validation**: Ensure completeness and consistency of extracted data
4. **Criteria Weighting**: Capture evaluation criteria with percentage weights

**Output**: `outputs/rfp_analysis/smart_parking_extracted.json`
```json
{
  "project_name": "Smart Parking System Implementation",
  "budget_limit": 450000,
  "timeline_limit": "120 days",
  "evaluation_criteria": {
    "Technical Capability": 0.35,
    "Cost Effectiveness": 0.25,
    "Timeline Feasibility": 0.20,
    "Company Experience": 0.15,
    "Post-Deployment Support": 0.05
  },
  "mandatory_requirements": [...],
  "scope_items": [...]
}
```

### **📊 Shape 2: Vendor Proposal Analysis**  
**Purpose**: Process all vendor proposals against RFP requirements

**Process**:
1. **Batch Processing**: Automatically scan all PDFs in `data/proposals/`
2. **RFP-Guided Extraction**: Use RFP context to guide vendor data extraction
3. **Compliance Assessment**: Check mandatory requirements compliance
4. **Scope Coverage Analysis**: Map vendor offerings to RFP scope items

**Output**: Individual analysis files per vendor
```json
{
  "vendor_name": "TechNova FZ-LLC", 
  "total_cost": 448000,
  "timeline": "120 days",
  "scope_coverage": "10/10 items",
  "compliance_status": "6/6 requirements met",
  "confidence_level": "high"
}
```

### **🏆 Shape 3: Advanced AI Evaluation & Scoring**
**Purpose**: Generate comprehensive vendor rankings with detailed justification

**Process**:
1. **Multi-Criteria Scoring**: AI evaluates each vendor on all RFP criteria (1-10 scale)
2. **Weighted Calculation**: Apply RFP criteria weights to raw scores
3. **Confidence Assessment**: AI self-evaluation of scoring reliability
4. **Advanced Analytics**: Performance gaps, risk assessment, competitive analysis
5. **Executive Insights**: AI-generated strategic recommendations

**Output**: Professional procurement reports and detailed analytics

## 🛠️ Technology Stack

### **Frontend & UI**
- **Streamlit**: Interactive web application framework
- **Responsive Design**: Full-width, modern browser optimization
- **Real-time Updates**: Live progress indicators and dynamic content

### **Core AI & ML**
- **OpenAI GPT-4o**: Primary AI model for content understanding and evaluation
- **LangChain 0.3.26+**: Document processing, AI integration, and prompt management
- **Python-dotenv**: Environment configuration management

### **Document Processing**
- **PyPDF**: PDF parsing and text extraction
- **LangChain Document Loaders**: Structured document handling

### **Development & Deployment**
- **Python 3.13**: Core runtime environment
- **UV Package Manager**: Fast dependency management and virtual environments
- **Pydantic**: Data validation and schema enforcement

### **Output Generation**
- **JSON**: Structured data exports for integration
- **CSV**: Spreadsheet-compatible vendor comparison matrices
- **Text Reports**: Executive summaries and detailed analytics
- **Interactive Tables**: Streamlit-powered data visualization

## 📁 Project Structure

```
ai-procurements-agent/
├── 🌐 Web Interface
│   └── streamlit_app.py          # Interactive Streamlit application
│
├── 🎯 Core Pipeline
│   ├── main.py                    # Complete pipeline orchestrator
│   ├── rfp_analyzer.py           # Shape 1: RFP extraction
│   ├── vendor_analyzer.py        # Shape 2: Vendor processing
│   └── evaluation_engine.py      # Shape 3: AI evaluation
│
├── 🧠 AI Components  
│   ├── rfp_schema.py             # Adaptive RFP data schema
│   └── evaluation_prompts.py     # Specialized AI prompts
│
├── 📂 Data & Configuration
│   ├── data/
│   │   ├── smart_parking_rfp.pdf    # Sample RFP document
│   │   └── proposals/               # Vendor proposal PDFs
│   │       ├── acme_corp_proposal.pdf
│   │       ├── Nexora_Proposal.pdf
│   │       ├── Stratiform_Proposal.pdf
│   │       └── TechNova_Proposal.pdf
│   ├── config.yaml               # System configuration
│   └── .env                      # API keys and settings
│
├── 📊 Generated Outputs
│   └── outputs/
│       ├── rfp_analysis/         # RFP extraction results
│       ├── proposal_analysis/    # Individual vendor analyses  
│       ├── evaluations/          # Detailed AI evaluations
│       └── reports/              # Executive reports & analytics
│
└── 📚 Documentation
    ├── README.md                 # This comprehensive guide
    ├── CLAUDE.md                 # Development history
    └── LICENSE                   # Project license
```

## 🚀 Installation & Usage

### **Prerequisites**
- Python 3.13+
- OpenAI API Key (for full AI evaluation)
- UV package manager (recommended) or pip

### **Quick Start - Web Interface**
```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-procurements-agent

# 2. Install dependencies
uv sync
# OR with pip: pip install -r requirements.txt

# 3. Launch web interface (works without API key for demo)
uv run streamlit run streamlit_app.py

# 4. Access application
# Open browser to: http://localhost:8501
```

### **Full Pipeline Setup**
```bash
# 3. Configure environment (for full AI features)
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env

# 4. Run complete pipeline
uv run python main.py
# OR: python main.py
```

### **Input Requirements**
- **Vendor Proposals**: Place all proposal PDFs in `data/proposals/`
- **Web Interface**: No additional setup required for basic analysis
- **OpenAI API Key**: Required only for full AI evaluation features

## 📈 System Outputs & Reports

### **🌐 Web Interface Output**
- **📊 Interactive Ranking Table**: Live vendor comparison with all criteria scores
- **📋 Detailed Vendor Analysis**: Expandable sections with proposal content
- **🎯 Executive Summary**: AI-generated insights and recommendations
- **📈 Real-time Processing**: Progress indicators and status updates

### **📋 Executive Summary** (`executive_procurement_report.txt`)
- **Top 3 Vendor Rankings** with scores and recommendations
- **Recommended Vendor Details** with justification
- **Key Performance Metrics** across all criteria

### **📊 Advanced Analytics** (`advanced_comparison_analysis.txt`)
- **Performance Gap Analysis**: Score differences across vendors and criteria
- **Risk & Confidence Assessment**: Procurement risk evaluation matrix
- **Vendor Strengths Analysis**: Top performers by criteria
- **AI Executive Insights**: Strategic recommendations and next steps
- **Detailed Justification**: Complete reasoning for recommendations

### **📈 Comparison Matrix** (`vendor_comparison_matrix.csv`)
- **Spreadsheet-ready data** for further analysis
- **All scores and weights** in structured format
- **Confidence levels** and risk assessments

### **🔍 Detailed Evaluations** (JSON files per vendor)
- **Criteria-by-criteria scoring** with justifications
- **Strengths and weaknesses** identification
- **Confidence assessment** for each evaluation
- **Complete audit trail** for procurement decisions

## 🎯 Real-World Testing Results

**Test Case**: Smart Parking System RFP (450,000 SAR budget, 120-day timeline)
**Vendors Evaluated**: 4 companies with varied proposals and completeness

### **Sample Results**
```
VENDOR EVALUATION MATRIX
==================================================================
Vendor                    | Technical | Cost | Timeline | Experience | Support | Total | Rank
--------------------------|-----------|------|----------|------------|---------|-------|------
TechNova FZ-LLC          |    9      |   8  |    8     |     8      |    9    |  8.4  |  1
UrbanIQ Solutions FZ-LLC |    8      |   8  |    7     |     8      |    8    |  7.8  |  2  
Nexora Technologies      |    9      |   6  |    5     |     8      |    4    |  7.0  |  3
Stratiform Solutions     |    6      |   6  |    6     |     8      |    6    |  6.8  |  4
```

**AI Recommendation**: TechNova FZ-LLC selected with 8.4/10 score
**Key Factors**: Strong technical capability, excellent support, within budget
**Confidence Level**: HIGH across all evaluation criteria

## 💡 Key Innovation Features

### **🌐 Interactive Web Experience**
- **One-Click Analysis**: Simple interface for complex procurement evaluation
- **Real-time Progress**: Live updates during analysis processing
- **Comprehensive Display**: Rankings, detailed vendor analysis, and insights in one view
- **Responsive Design**: Optimized for desktop and tablet use

### **⚡ Flexible Evaluation Modes**
- **Full AI Mode**: Complete GPT-4o analysis with detailed justification
- **Heuristic Mode**: Fast rule-based evaluation for quick assessments
- **Demo Mode**: Works without API keys for testing and demonstrations

### **🧠 Intelligent Prompt Engineering**
- **Specialized Prompts**: Different AI prompts for each evaluation criteria
- **Context-Aware**: RFP requirements guide vendor evaluation
- **Confidence Scoring**: AI self-assessment of evaluation reliability

### **⚖️ Sophisticated Scoring System**
- **Weighted Evaluation**: Respects RFP criteria importance (35% technical, 25% cost, etc.)
- **Standardized Scale**: Consistent 1-10 scoring across all criteria
- **Justification Required**: Every score includes detailed reasoning

### **📊 Advanced Analytics**
- **Performance Gap Analysis**: Identifies competitive advantages and weaknesses
- **Risk Assessment**: Procurement risk based on confidence and scores
- **Executive Insights**: AI-generated strategic recommendations

## 🎓 Capstone Project Value

### **Technical Demonstrations**
- **Modern Web Interface**: Professional Streamlit application development
- **Large Language Model Integration**: Practical GPT-4o implementation
- **Document AI**: PDF processing and content understanding
- **Structured Data Extraction**: Unstructured to structured data transformation
- **AI-Driven Decision Making**: Objective evaluation with explainable reasoning
- **Responsive UI Design**: Full-width, user-friendly interface

### **Business Impact**
- **Process Automation**: Eliminates weeks of manual procurement analysis
- **User-Friendly Interface**: Non-technical users can perform complex analysis
- **Objective Decision-Making**: Reduces bias in vendor selection
- **Audit Compliance**: Complete justification and decision trail
- **Scalable Solution**: Handles multiple RFPs and vendors simultaneously

### **Software Engineering Practices**
- **Dual Interface Architecture**: Web and command-line interfaces
- **Modular Design**: Clean separation of concerns across pipeline stages
- **Error Handling**: Graceful degradation and confidence-based reliability
- **Professional Output**: Enterprise-grade reports and documentation
- **Extensible Design**: Easy to add new evaluation criteria or output formats

## 🚀 Future Enhancements

### **Near-Term Improvements**
- **File Upload Interface**: Upload RFPs and proposals via web browser
- **Multi-RFP Support**: Process multiple procurement projects simultaneously
- **Custom Criteria**: Allow dynamic evaluation criteria configuration
- **Export Features**: Download results in multiple formats

### **Advanced Features**
- **Natural Language Q&A**: Ask questions about vendor proposals
- **Comparative Analysis**: Side-by-side vendor comparison tools
- **Market Intelligence**: Vendor performance tracking across RFPs
- **Predictive Analytics**: Success probability modeling

## 🔧 Configuration Options

### **Environment Variables** (`.env`)
```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_TEMPERATURE=0.1                    # AI consistency (0.0-1.0)
MAX_TOKENS=2000                           # AI response length limit
```

### **System Configuration** (`config.yaml`)
```yaml
evaluation:
  scoring_scale: "1-10"
  confidence_threshold: "medium"
  
output:
  formats: ["json", "csv", "txt"]
  include_justifications: true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 Project Achievement Summary

✅ **Interactive Web Interface**: Professional Streamlit application for easy procurement analysis  
✅ **Complete Procurement Pipeline**: RFP → Vendor Analysis → AI Evaluation  
✅ **Dual Interface Design**: Both web and command-line access  
✅ **Enterprise-Grade Output**: Professional reports ready for C-level decisions  
✅ **AI-Powered Intelligence**: Advanced scoring with detailed justification  
✅ **Real-World Testing**: Successfully evaluated 4 vendors on actual RFP  
✅ **Scalable Architecture**: Modular design supporting various procurement scenarios  
✅ **User-Friendly Design**: Accessible to non-technical procurement professionals  

**Built for AI Engineering Bootcamp Capstone Project**  
*Demonstrating practical AI applications in enterprise procurement workflows with modern web interface*