"""
PDF processing module for the AI Procurement Agent
Handles loading and extracting data from vendor proposal PDFs
"""

import os
import glob
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# LangChain imports for PDF processing
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_json_output_path(pdf_path: str, output_directory: str = "outputs") -> str:
    """
    Get the JSON output file path for a given PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_directory: Directory where JSON files are saved
        
    Returns:
        Path to the corresponding JSON output file
    """
    pdf_name = Path(pdf_path).stem
    json_filename = f"{pdf_name}_extracted.json"
    return os.path.join(output_directory, json_filename)


def is_already_processed(pdf_path: str, output_directory: str = "outputs") -> bool:
    """
    Check if a PDF file has already been processed by looking for its JSON output.
    
    Args:
        pdf_path: Path to the PDF file
        output_directory: Directory where JSON files are saved
        
    Returns:
        True if already processed, False otherwise
    """
    json_path = get_json_output_path(pdf_path, output_directory)
    return os.path.exists(json_path)


def save_to_json(proposal_data: Dict[str, Any], pdf_path: str, output_directory: str = "outputs") -> None:
    """
    Save extracted proposal data to a JSON file.
    
    Args:
        proposal_data: Extracted proposal data
        pdf_path: Original PDF file path
        output_directory: Directory where JSON files are saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Get JSON output path
    json_path = get_json_output_path(pdf_path, output_directory)
    
    # Add metadata about the original PDF
    output_data = {
        "metadata": {
            "source_pdf": pdf_path,
            "extracted_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(pdf_path)
        },
        "extracted_data": proposal_data
    }
    
    # Save to JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved extracted data to: {json_path}")


def load_from_json(pdf_path: str, output_directory: str = "outputs") -> Dict[str, Any]:
    """
    Load already extracted proposal data from JSON file.
    
    Args:
        pdf_path: Path to the PDF file
        output_directory: Directory where JSON files are saved
        
    Returns:
        Previously extracted proposal data
    """
    json_path = get_json_output_path(pdf_path, output_directory)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["extracted_data"]


def load_pdf_files(pdf_directory: str = "data/proposals") -> List[Dict[str, Any]]:
    """
    Load all PDF files from the specified directory and extract basic info.
    
    Args:
        pdf_directory: Directory containing PDF proposal files
        
    Returns:
        List of dictionaries with PDF metadata and content
    """
    pdf_files = glob.glob(f"{pdf_directory}/*.pdf")
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}/")
        return []
    
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    
    processed_pdfs = []
    
    for pdf_path in pdf_files:
        try:
            # Extract vendor name from filename
            vendor_name = Path(pdf_path).stem.replace("_", " ").title()
            
            # Load PDF using LangChain
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Combine all pages into single text
            full_text = "\n\n".join([doc.page_content for doc in documents])
            
            pdf_info = {
                "file_path": pdf_path,
                "vendor_name": vendor_name,
                "page_count": len(documents),
                "content": full_text,
                "file_size": os.path.getsize(pdf_path)
            }
            
            processed_pdfs.append(pdf_info)
            print(f"✅ Loaded {vendor_name}: {len(documents)} pages, {len(full_text)} characters")
            
        except Exception as e:
            print(f"❌ Error loading {pdf_path}: {e}")
            continue
    
    return processed_pdfs


def extract_proposal_data_simple(pdf_info: Dict[str, Any], proposal_id: int) -> Dict[str, Any]:
    """
    AI-powered extraction using GPT-4o to understand and extract proposal data.
    
    Args:
        pdf_info: Dictionary containing PDF information and content
        proposal_id: Unique ID for this proposal
        
    Returns:
        Structured proposal data matching VendorProposal schema
    """
    import os
    from dotenv import load_dotenv
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    from langchain.chains import LLMChain
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Define the structured output model
    class ProposalExtraction(BaseModel):
        vendor_name: str = Field(description="Name of the vendor/company submitting the proposal")
        project_name: str = Field(description="Name or title of the proposed project")
        price: float = Field(description="Total project price/cost in dollars (extract number only)")
        delivery_timeline: str = Field(description="Project timeline, delivery schedule, duration, milestones")
        scope_summary: str = Field(description="Summary of project scope, deliverables, services offered")
        risks: str = Field(description="Identified risks, challenges, limitations, or concerns mentioned")
    
    # Initialize LLM with GPT-4o and parser
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    output_parser = PydanticOutputParser(pydantic_object=ProposalExtraction)
    
    # Create AI extraction prompt
    extraction_prompt = PromptTemplate(
        template="""
        You are an expert procurement analyst. Analyze this vendor proposal and extract the key information.
        
        Read the entire document carefully and extract:
        1. Vendor/Company name
        2. Project name/title 
        3. Total project price (as a number in dollars)
        4. Delivery timeline and schedule
        5. Project scope and deliverables
        6. Risks, challenges, or limitations mentioned
        
        Be thorough - scan the entire document for this information as it may appear anywhere.
        For pricing, look for the total project cost, not individual line items.
        
        {format_instructions}
        
        DOCUMENT CONTENT:
        {document_content}
        
        EXTRACTED INFORMATION:
        """,
        input_variables=["document_content"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )
    
    # Create LLM chain
    extraction_chain = LLMChain(
        llm=llm,
        prompt=extraction_prompt,
        output_parser=output_parser
    )
    
    try:
        # Use AI to extract information
        print(f"🤖 Using AI to analyze proposal content...")
        extracted = extraction_chain.run(document_content=pdf_info["content"])
        
        return {
            "id": proposal_id,
            "vendor_name": extracted.vendor_name,
            "project_name": extracted.project_name,
            "time_stamp": datetime.now().isoformat(),
            "price": extracted.price,
            "delivery_timeline": extracted.delivery_timeline,
            "scope_summary": extracted.scope_summary,
            "risks": extracted.risks
        }
        
    except Exception as e:
        print(f"❌ AI extraction failed: {e}")
        # Fallback to basic extraction if AI fails
        return {
            "id": proposal_id,
            "vendor_name": pdf_info.get("vendor_name", "Unknown Vendor"),
            "project_name": "Project Analysis Failed",
            "time_stamp": datetime.now().isoformat(),
            "price": 0.0,
            "delivery_timeline": "Could not extract timeline",
            "scope_summary": "Could not extract scope",
            "risks": "Could not extract risks"
        }


# All regex helper functions removed - now using AI extraction!


def process_pdf_proposals(pdf_directory: str = "data/proposals") -> List[Dict[str, Any]]:
    """
    Complete pipeline to process PDF proposals into structured data.
    
    Args:
        pdf_directory: Directory containing PDF proposal files
        
    Returns:
        List of structured proposal data ready for Superlinked indexing
    """
    print("\n📄 Starting PDF processing pipeline...")
    
    # Load PDF files
    pdf_files = load_pdf_files(pdf_directory)
    if not pdf_files:
        return []
    
    # Extract structured data from each PDF
    proposals = []
    processed_count = 0
    skipped_count = 0
    
    for i, pdf_info in enumerate(pdf_files, 1):
        print(f"\n🔍 Processing {pdf_info['vendor_name']}...")
        
        # Check if already processed
        if is_already_processed(pdf_info["file_path"]):
            print(f"⏭️  Skipping {pdf_info['vendor_name']} (already processed)")
            skipped_count += 1
            
            # Load from JSON if already processed
            try:
                proposal_data = load_from_json(pdf_info["file_path"])
                print(f"📁 Loaded from JSON: {pdf_info['vendor_name']}")
            except Exception as e:
                print(f"❌ Error loading JSON for {pdf_info['vendor_name']}: {e}")
                continue
        else:
            # Extract and save to JSON
            proposal_data = extract_proposal_data_simple(pdf_info, i)
            save_to_json(proposal_data, pdf_info["file_path"])
            processed_count += 1
            
            # Show extracted data only for newly processed files
            print(f"✅ Extracted data:")
            print(f"   • Price: ${proposal_data['price']:,.0f}")
            print(f"   • Timeline: {proposal_data['delivery_timeline'][:100]}...")
            print(f"   • Scope: {proposal_data['scope_summary'][:100]}...")
            print(f"   • Risks: {proposal_data['risks'][:100]}...")
        
        proposals.append(proposal_data)
    
    # Summary
    print(f"\n🎯 Processing Summary:")
    print(f"   • Total files found: {len(pdf_files)}")
    print(f"   • Newly processed: {processed_count}")
    print(f"   • Skipped (already processed): {skipped_count}")
    print(f"   • Total proposals available: {len(proposals)}")
    
    return proposals


def run_pdf_tests(app, procurement_query, sl, proposals: List[Dict[str, Any]]):
    """
    Run search tests on PDF-extracted proposal data.
    
    Args:
        app: Superlinked app instance
        procurement_query: Query object for searching
        sl: Superlinked framework
        proposals: List of proposal data from PDFs
    """
    print("\n🔍 Testing PDF-based search functionality...")
    
    if not proposals:
        print("❌ No proposals to search")
        return
    
    # Test 1: Search for any content in the actual proposals
    print("\n1. Searching for 'project development':")
    result1 = app.query(
        procurement_query,
        scope_query="project development",
        scope_weight=1.0,
        price_weight=0.0,
        risks_weight=0.0,
        limit=3
    )
    df1 = sl.PandasConverter.to_pandas(result1)
    print(f"Found {len(df1)} results:")
    for _, row in df1.iterrows():
        print(f"   • {row['vendor_name']}: {row['project_name']} (${row['price']:,.0f})")
    
    # Test 2: Search for risk-related content
    print("\n2. Searching for 'risk challenge':")
    result2 = app.query(
        procurement_query,
        risks_query="risk challenge issue",
        scope_weight=0.0,
        price_weight=0.0,
        risks_weight=1.0,
        limit=3
    )
    df2 = sl.PandasConverter.to_pandas(result2)
    print(f"Found {len(df2)} results:")
    for _, row in df2.iterrows():
        print(f"   • {row['vendor_name']}: {row['risks'][:100]}...")
    
    # Test 3: Show all extracted proposals
    print("\n3. All extracted proposals:")
    for proposal in proposals:
        print(f"   • {proposal['vendor_name']}: ${proposal['price']:,.0f} - {proposal['scope_summary'][:80]}...")
    
    print("\n🎉 PDF processing tests completed successfully!") 