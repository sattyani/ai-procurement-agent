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
        print(f"No PDF files found in {pdf_directory}/")
        return []
    
    print(f"Loading {len(pdf_files)} vendor proposals...")
    
    processed_pdfs = []
    
    for pdf_path in pdf_files:
        try:
            # Extract vendor name from filename
            vendor_name = Path(pdf_path).stem.replace("_", " ").title()
            
            # Load PDF using LangChain (suppress warnings)
            import warnings
            import sys
            import os
            from contextlib import redirect_stderr
            
            with warnings.catch_warnings(), redirect_stderr(open(os.devnull, 'w')):
                warnings.simplefilter("ignore")
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
            print(f"   OK: {vendor_name}")
            
        except Exception as e:
            print(f"   ERROR: {pdf_path}: {e}")
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
        print(f"AI extraction failed: {e}")
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
    print("\nStarting AI Procurement Agent...")
    
    # Load PDF files
    pdf_files = load_pdf_files(pdf_directory)
    if not pdf_files:
        return []
    
    # Extract structured data from each PDF
    proposals = []
    processed_count = 0
    skipped_count = 0
    
    print(f"\nExtracting proposal data...")
    
    for i, pdf_info in enumerate(pdf_files, 1):
        vendor_name = pdf_info['vendor_name']
        
        # Check if already processed
        if is_already_processed(pdf_info["file_path"]):
            skipped_count += 1
            
            # Load from JSON if already processed
            try:
                proposal_data = load_from_json(pdf_info["file_path"])
                print(f"   {vendor_name} (cached)")
            except Exception as e:
                print(f"   ERROR loading {vendor_name}: {e}")
                continue
        else:
            # Extract and save to JSON
            print(f"   Analyzing {vendor_name}...")
            proposal_data = extract_proposal_data_simple(pdf_info, i)
            save_to_json(proposal_data, pdf_info["file_path"])
            processed_count += 1
            
            print(f"   {vendor_name}: ${proposal_data['price']:,.0f}")
        
        proposals.append(proposal_data)
    
    # Summary - keep quiet for demo
    
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
    print("\nTesting PDF-based search functionality...")
    
    if not proposals:
        print("No proposals to search")
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
    
    print("\nPDF processing tests completed successfully!")


def analyze_risk_level(risks_text: str) -> str:
    """
    Analyze risk level based on risk description text.
    
    Args:
        risks_text: Risk description from proposal
        
    Returns:
        Risk level: "Low", "Medium", or "High"
    """
    risks_lower = risks_text.lower()
    
    # High risk indicators
    high_risk_keywords = [
        'delay', 'complex', 'challenge', 'difficult', 'uncertain', 
        'dependency', 'integration', 'compatibility', 'performance',
        'migration', 'overrun', 'issue', 'problem'
    ]
    
    # Low risk indicators  
    low_risk_keywords = [
        'straightforward', 'simple', 'proven', 'standard', 'reliable',
        'tested', 'stable', 'minimal', 'low'
    ]
    
    high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in risks_lower)
    low_risk_count = sum(1 for keyword in low_risk_keywords if keyword in risks_lower)
    
    if high_risk_count >= 3:
        return "High"
    elif high_risk_count >= 1 and low_risk_count == 0:
        return "Medium"
    elif low_risk_count >= 2:
        return "Low"
    else:
        return "Medium"


def extract_timeline_months(timeline_text: str) -> float:
    """
    Extract numeric timeline in months from timeline text.
    
    Args:
        timeline_text: Timeline description
        
    Returns:
        Timeline in months (float)
    """
    import re
    
    timeline_lower = timeline_text.lower()
    
    # Look for month patterns
    month_patterns = [
        r'(\d+)\s*months?',
        r'(\d+)\s*month',
        r'(\d+)\s*mo'
    ]
    
    for pattern in month_patterns:
        match = re.search(pattern, timeline_lower)
        if match:
            return float(match.group(1))
    
    # Look for week patterns
    week_patterns = [
        r'(\d+)\s*weeks?',
        r'(\d+)\s*week',
        r'(\d+)\s*wk'
    ]
    
    for pattern in week_patterns:
        match = re.search(pattern, timeline_lower)
        if match:
            return float(match.group(1)) / 4.33  # Convert weeks to months
    
    # Default if no pattern found
    return 6.0


def build_comparison_table(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build the main comparison table with all vendor data.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        Formatted comparison table
    """
    comparison_data = []
    
    # Sort by price for ranking
    sorted_by_price = sorted(proposals, key=lambda x: x["price"])
    price_ranks = {prop["vendor_name"]: i+1 for i, prop in enumerate(sorted_by_price)}
    
    for proposal in proposals:
        timeline_months = extract_timeline_months(proposal["delivery_timeline"])
        risk_level = analyze_risk_level(proposal["risks"])
        
        comparison_data.append({
            "vendor": proposal["vendor_name"],
            "project": proposal["project_name"],
            "price": proposal["price"],
            "price_rank": price_ranks[proposal["vendor_name"]],
            "timeline": proposal["delivery_timeline"],
            "timeline_months": timeline_months,
            "scope_preview": proposal["scope_summary"][:100] + "..." if len(proposal["scope_summary"]) > 100 else proposal["scope_summary"],
            "risk_level": risk_level,
            "risks_preview": proposal["risks"][:100] + "..." if len(proposal["risks"]) > 100 else proposal["risks"]
        })
    
    return comparison_data


def calculate_summary_stats(proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics across all proposals.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        Summary statistics dictionary
    """
    if not proposals:
        return {}
    
    prices = [p["price"] for p in proposals]
    timelines = [extract_timeline_months(p["delivery_timeline"]) for p in proposals]
    risk_levels = [analyze_risk_level(p["risks"]) for p in proposals]
    
    return {
        "price_analysis": {
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "price_spread": max(prices) - min(prices)
        },
        "timeline_analysis": {
            "fastest_delivery_months": min(timelines),
            "longest_delivery_months": max(timelines),
            "avg_timeline_months": sum(timelines) / len(timelines)
        },
        "risk_distribution": {
            "low_risk": risk_levels.count("Low"),
            "medium_risk": risk_levels.count("Medium"),
            "high_risk": risk_levels.count("High")
        }
    }


def generate_insights(proposals: List[Dict[str, Any]]) -> List[str]:
    """
    Generate key insights from proposal analysis.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        List of insight strings
    """
    if not proposals:
        return []
    
    insights = []
    
    # Price insights
    prices = [p["price"] for p in proposals]
    min_price = min(prices)
    max_price = max(prices)
    price_spread = max_price - min_price
    
    cheapest = min(proposals, key=lambda x: x["price"])
    most_expensive = max(proposals, key=lambda x: x["price"])
    
    insights.append(f"Price variation of ${price_spread:,.0f} between cheapest ({cheapest['vendor_name']}: ${min_price:,.0f}) and most expensive ({most_expensive['vendor_name']}: ${max_price:,.0f})")
    
    # Timeline insights
    timelines = [(p, extract_timeline_months(p["delivery_timeline"])) for p in proposals]
    fastest = min(timelines, key=lambda x: x[1])
    
    insights.append(f"{fastest[0]['vendor_name']} offers fastest delivery at {fastest[1]:.1f} months")
    
    # Risk insights
    high_risk_vendors = [p["vendor_name"] for p in proposals if analyze_risk_level(p["risks"]) == "High"]
    if high_risk_vendors:
        insights.append(f"High risk vendors: {', '.join(high_risk_vendors)}")
    
    # Scope insights
    avg_scope_length = sum(len(p["scope_summary"]) for p in proposals) / len(proposals)
    detailed_vendors = [p["vendor_name"] for p in proposals if len(p["scope_summary"]) > avg_scope_length * 1.5]
    if detailed_vendors:
        insights.append(f"Most detailed scope descriptions: {', '.join(detailed_vendors)}")
    
    return insights


def generate_rankings(proposals: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Generate rankings by different criteria.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        Rankings dictionary
    """
    if not proposals:
        return {}
    
    # Rank by price (lowest first)
    by_price = sorted(proposals, key=lambda x: x["price"])
    price_ranking = [p["vendor_name"] for p in by_price]
    
    # Rank by timeline (fastest first) 
    by_timeline = sorted(proposals, key=lambda x: extract_timeline_months(x["delivery_timeline"]))
    timeline_ranking = [p["vendor_name"] for p in by_timeline]
    
    # Rank by risk (lowest risk first)
    risk_order = {"Low": 1, "Medium": 2, "High": 3}
    by_risk = sorted(proposals, key=lambda x: risk_order[analyze_risk_level(x["risks"])])
    risk_ranking = [p["vendor_name"] for p in by_risk]
    
    return {
        "by_price": price_ranking,
        "by_timeline": timeline_ranking,
        "by_risk": risk_ranking
    }


def save_comparison_csv(comparison_table: List[Dict[str, Any]], output_dir: str) -> str:
    """
    Save comparison table as CSV file.
    
    Args:
        comparison_table: Comparison data
        output_dir: Output directory
        
    Returns:
        Path to saved CSV file
    """
    import csv
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = os.path.join(output_dir, f"vendor_comparison_{timestamp}.csv")
    
    if comparison_table:
        fieldnames = ["vendor", "project", "price", "price_rank", "timeline", "timeline_months", "risk_level", "scope_preview"]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in comparison_table:
                # Only write the fields we want in CSV
                csv_row = {field: row.get(field, "") for field in fieldnames}
                writer.writerow(csv_row)
    
    return csv_path


def generate_comparison_report(proposals: List[Dict[str, Any]], output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Generate comprehensive vendor comparison report.
    
    Args:
        proposals: List of proposal dictionaries from PDF processing
        output_dir: Directory to save report files
        
    Returns:
        Complete comparison report dictionary
    """
    if not proposals:
        return {}
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the complete report
    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_vendors": len(proposals),
            "report_type": "vendor_comparison"
        },
        "comparison_table": build_comparison_table(proposals),
        "summary_statistics": calculate_summary_stats(proposals),
        "key_insights": generate_insights(proposals),
        "rankings": generate_rankings(proposals)
    }
    
    # Save JSON report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f"vendor_comparison_{timestamp}.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Save CSV version
    csv_path = save_comparison_csv(report["comparison_table"], output_dir)
    
    return report


def get_evaluation_profiles() -> Dict[str, Dict[str, float]]:
    """
    Get predefined evaluation profiles for different procurement scenarios.
    
    Returns:
        Dictionary of evaluation profiles with weights
    """
    return {
        "budget_focused": {
            "scope_weight": 0.2,
            "price_weight": 0.7,
            "risks_weight": 0.1,
            "description": "Optimizes for lowest cost while maintaining basic scope and risk requirements"
        },
        "risk_averse": {
            "scope_weight": 0.3,
            "price_weight": 0.1,
            "risks_weight": 0.6,
            "description": "Prioritizes low-risk vendors even at higher cost"
        },
        "scope_perfect": {
            "scope_weight": 0.8,
            "price_weight": 0.1,
            "risks_weight": 0.1,
            "description": "Finds vendors with best scope match regardless of price"
        },
        "balanced": {
            "scope_weight": 0.4,
            "price_weight": 0.3,
            "risks_weight": 0.3,
            "description": "Balanced evaluation across all criteria"
        },
        "fast_delivery": {
            "scope_weight": 0.5,
            "price_weight": 0.2,
            "risks_weight": 0.3,
            "description": "Optimizes for quick delivery with good scope match"
        }
    }


def recommend_best_proposals(app, procurement_query, sl, proposals: List[Dict[str, Any]], 
                           evaluation_profile: str = "balanced", 
                           scope_query: str = "", 
                           risks_query: str = "low risk reliable stable",
                           limit: int = 5) -> Dict[str, Any]:
    """
    Generate weighted recommendations using Superlinked evaluation.
    
    Args:
        app: Superlinked app instance
        procurement_query: Query object for searching
        sl: Superlinked framework
        proposals: List of proposal dictionaries
        evaluation_profile: Profile name from get_evaluation_profiles()
        scope_query: Specific scope requirements to search for
        risks_query: Risk-related search terms
        limit: Number of recommendations to return
        
    Returns:
        Recommendation report with ranked proposals
    """
    profiles = get_evaluation_profiles()
    if evaluation_profile not in profiles:
        evaluation_profile = "balanced"
    
    profile = profiles[evaluation_profile]
    
    # If no specific scope query provided, create a general one
    if not scope_query:
        # Extract common scope terms from all proposals
        all_scopes = " ".join([p["scope_summary"] for p in proposals])
        scope_query = "project development services software"
    
    try:
        # Use Superlinked with weighted evaluation
        result = app.query(
            procurement_query,
            scope_query=scope_query,
            risks_query=risks_query,
            scope_weight=profile["scope_weight"],
            price_weight=profile["price_weight"],
            risks_weight=profile["risks_weight"],
            limit=limit
        )
        
        # Convert to DataFrame for easier handling
        df = sl.PandasConverter.to_pandas(result)
        
        # Create recommendation report
        recommendations = []
        for i, (_, row) in enumerate(df.iterrows(), 1):
            recommendation = {
                "rank": i,
                "vendor_name": row["vendor_name"],
                "project_name": row["project_name"],
                "price": row["price"],
                "delivery_timeline": row["delivery_timeline"],
                "scope_summary": row["scope_summary"][:150] + "..." if len(row["scope_summary"]) > 150 else row["scope_summary"],
                "risks": row["risks"][:150] + "..." if len(row["risks"]) > 150 else row["risks"],
                "similarity_score": getattr(row, '_score', 0.0) if hasattr(row, '_score') else 0.0
            }
            recommendations.append(recommendation)
        
        # Calculate evaluation scores
        evaluation_scores = calculate_evaluation_scores(proposals, profile)
        
        # Merge similarity scores with evaluation scores
        for rec in recommendations:
            vendor_eval = next((e for e in evaluation_scores if e["vendor_name"] == rec["vendor_name"]), {})
            rec.update(vendor_eval)
        
        recommendation_report = {
            "evaluation_metadata": {
                "profile_used": evaluation_profile,
                "profile_description": profile["description"],
                "weights_applied": {
                    "scope_weight": profile["scope_weight"],
                    "price_weight": profile["price_weight"], 
                    "risks_weight": profile["risks_weight"]
                },
                "scope_query": scope_query,
                "risks_query": risks_query,
                "generated_at": datetime.now().isoformat()
            },
            "recommendations": recommendations,
            "evaluation_summary": generate_recommendation_insights(recommendations, evaluation_profile)
        }
        
        return recommendation_report
        
    except Exception as e:
        print(f"   ERROR generating recommendations: {e}")
        return {"error": str(e), "recommendations": []}


def calculate_evaluation_scores(proposals: List[Dict[str, Any]], profile: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Calculate normalized evaluation scores for each proposal based on profile weights.
    
    Args:
        proposals: List of proposal dictionaries
        profile: Evaluation profile with weights
        
    Returns:
        List of evaluation scores for each vendor
    """
    if not proposals:
        return []
    
    evaluation_scores = []
    
    # Normalize price scores (lower is better)
    prices = [p["price"] for p in proposals]
    max_price = max(prices)
    min_price = min(prices)
    price_range = max_price - min_price if max_price != min_price else 1
    
    # Normalize timeline scores (shorter is better)
    timelines = [extract_timeline_months(p["delivery_timeline"]) for p in proposals]
    max_timeline = max(timelines)
    min_timeline = min(timelines)
    timeline_range = max_timeline - min_timeline if max_timeline != min_timeline else 1
    
    # Calculate risk scores (lower risk is better)
    risk_scores = {"Low": 1.0, "Medium": 0.6, "High": 0.2}
    
    for i, proposal in enumerate(proposals):
        # Price score (normalized, lower price = higher score)
        price_score = 1.0 - ((proposal["price"] - min_price) / price_range) if price_range > 0 else 1.0
        
        # Timeline score (normalized, shorter timeline = higher score)
        timeline_score = 1.0 - ((timelines[i] - min_timeline) / timeline_range) if timeline_range > 0 else 1.0
        
        # Risk score
        risk_level = analyze_risk_level(proposal["risks"])
        risk_score = risk_scores.get(risk_level, 0.5)
        
        # Scope score (length and detail as proxy for thoroughness)
        scope_length = len(proposal["scope_summary"])
        avg_scope_length = sum(len(p["scope_summary"]) for p in proposals) / len(proposals)
        scope_score = min(1.0, scope_length / (avg_scope_length * 1.2)) if avg_scope_length > 0 else 0.5
        
        # Weighted final score
        final_score = (
            scope_score * profile["scope_weight"] +
            price_score * profile["price_weight"] +
            risk_score * profile["risks_weight"]
        )
        
        evaluation_scores.append({
            "vendor_name": proposal["vendor_name"],
            "price_score": round(price_score, 3),
            "timeline_score": round(timeline_score, 3),
            "risk_score": round(risk_score, 3),
            "scope_score": round(scope_score, 3),
            "final_score": round(final_score, 3),
            "risk_level": risk_level
        })
    
    return evaluation_scores


def generate_recommendation_insights(recommendations: List[Dict[str, Any]], profile: str) -> List[str]:
    """
    Generate insights from recommendation results.
    
    Args:
        recommendations: List of ranked recommendations
        profile: Evaluation profile used
        
    Returns:
        List of insight strings
    """
    if not recommendations:
        return ["No recommendations available"]
    
    insights = []
    
    # Top recommendation insight
    top_vendor = recommendations[0]
    insights.append(f"Top recommendation: {top_vendor['vendor_name']} with final score of {top_vendor.get('final_score', 'N/A')}")
    
    # Price insights
    if profile == "budget_focused":
        cheapest = min(recommendations, key=lambda x: x["price"])
        insights.append(f"Most cost-effective option: {cheapest['vendor_name']} at ${cheapest['price']:,.0f}")
    
    # Risk insights
    if profile == "risk_averse":
        low_risk_vendors = [r for r in recommendations if r.get("risk_level") == "Low"]
        if low_risk_vendors:
            insights.append(f"Low-risk vendors available: {', '.join([v['vendor_name'] for v in low_risk_vendors])}")
        else:
            insights.append("No low-risk vendors available in current selection")
    
    # Score distribution
    scores = [r.get("final_score", 0) for r in recommendations if r.get("final_score")]
    if scores:
        avg_score = sum(scores) / len(scores)
        insights.append(f"Average evaluation score: {avg_score:.3f}, Top score: {max(scores):.3f}")
    
    # Price spread in top recommendations
    top_3_prices = [r["price"] for r in recommendations[:3]]
    if len(top_3_prices) > 1:
        price_spread = max(top_3_prices) - min(top_3_prices)
        insights.append(f"Price range in top 3 recommendations: ${price_spread:,.0f}")
    
    return insights


def save_recommendation_report(recommendation_report: Dict[str, Any], output_dir: str = "outputs") -> str:
    """
    Save recommendation report to JSON file.
    
    Args:
        recommendation_report: Complete recommendation report
        output_dir: Output directory
        
    Returns:
        Path to saved report file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    profile = recommendation_report.get("evaluation_metadata", {}).get("profile_used", "unknown")
    report_path = os.path.join(output_dir, f"recommendations_{profile}_{timestamp}.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(recommendation_report, f, indent=2, ensure_ascii=False)
    
    return report_path


def run_recommendation_tests(app, procurement_query, sl, proposals: List[Dict[str, Any]]):
    """
    Test different recommendation profiles and show results.
    
    Args:
        app: Superlinked app instance
        procurement_query: Query object for searching
        sl: Superlinked framework
        proposals: List of proposal data
    """
    print("\nTesting recommendation system with different profiles...")
    
    if not proposals:
        print("No proposals available for recommendations")
        return
    
    profiles = get_evaluation_profiles()
    
    for profile_name, profile_info in profiles.items():
        print(f"\n--- {profile_name.upper()} PROFILE ---")
        print(f"Description: {profile_info['description']}")
        print(f"Weights: Scope={profile_info['scope_weight']}, Price={profile_info['price_weight']}, Risk={profile_info['risks_weight']}")
        
        # Generate recommendations
        recommendations = recommend_best_proposals(
            app, procurement_query, sl, proposals,
            evaluation_profile=profile_name,
            limit=3
        )
        
        if recommendations.get("recommendations"):
            print("Top 3 Recommendations:")
            for rec in recommendations["recommendations"][:3]:
                print(f"  {rec['rank']}. {rec['vendor_name']}: ${rec['price']:,.0f} (Score: {rec.get('final_score', 'N/A')})")
        
        # Save report
        if recommendations and not recommendations.get("error"):
            report_path = save_recommendation_report(recommendations)
            print(f"Saved: {report_path}")
    
    print("\nRecommendation testing completed!")


def detect_scope_mismatches(proposals: List[Dict[str, Any]]) -> List[str]:
    """
    Detect potential scope mismatches between vendor proposals.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        List of scope mismatch issues
    """
    issues = []
    
    if not proposals:
        return issues
    
    # Extract project types from project names and scope
    project_keywords = []
    for proposal in proposals:
        project_text = f"{proposal['project_name']} {proposal['scope_summary']}".lower()
        project_keywords.append(project_text)
    
    # Check for major keyword mismatches
    common_keywords = ['portal', 'management', 'vendor', 'web', 'dashboard']
    ai_keywords = ['ai', 'machine learning', 'artificial intelligence', 'model', 'ml']
    
    portal_vendors = []
    ai_vendors = []
    
    for i, proposal in enumerate(proposals):
        text = project_keywords[i]
        
        if any(keyword in text for keyword in common_keywords):
            portal_vendors.append(proposal['vendor_name'])
        
        if any(keyword in text for keyword in ai_keywords):
            ai_vendors.append(proposal['vendor_name'])
    
    # Detect mismatches
    if ai_vendors and portal_vendors:
        issues.append(f"Scope mismatch detected: {', '.join(ai_vendors)} proposing AI services while {', '.join(portal_vendors)} proposing portal development")
    
    # Check for project name consistency
    project_names = [p['project_name'].lower() for p in proposals]
    unique_types = set()
    for name in project_names:
        if 'portal' in name:
            unique_types.add('portal')
        elif 'ai' in name or 'artificial' in name:
            unique_types.add('ai')
        elif 'development' in name:
            unique_types.add('development')
    
    if len(unique_types) > 1:
        issues.append("Multiple project types identified - verify all vendors understand requirements")
    
    return issues


def identify_red_flags(proposals: List[Dict[str, Any]], recommendations: Dict[str, Any] = None) -> List[str]:
    """
    Identify potential red flags in vendor proposals.
    
    Args:
        proposals: List of proposal dictionaries
        recommendations: Optional recommendation data
        
    Returns:
        List of red flag warnings
    """
    red_flags = []
    
    if not proposals:
        return red_flags
    
    # Risk concentration analysis
    high_risk_count = sum(1 for p in proposals if analyze_risk_level(p["risks"]) == "High")
    risk_percentage = high_risk_count / len(proposals)
    
    if risk_percentage >= 0.75:
        red_flags.append(f"High risk concentration: {high_risk_count}/{len(proposals)} vendors rated high risk")
    
    # Timeline realism check
    timelines = [extract_timeline_months(p["delivery_timeline"]) for p in proposals]
    min_timeline = min(timelines)
    avg_timeline = sum(timelines) / len(timelines)
    
    if min_timeline < avg_timeline * 0.6:  # If shortest is <60% of average
        fastest_vendor = min(proposals, key=lambda x: extract_timeline_months(x["delivery_timeline"]))
        red_flags.append(f"{fastest_vendor['vendor_name']} timeline ({min_timeline:.1f} months) seems aggressive compared to average ({avg_timeline:.1f} months)")
    
    # Price outlier detection
    prices = [p["price"] for p in proposals]
    min_price = min(prices)
    max_price = max(prices)
    price_ratio = max_price / min_price if min_price > 0 else 1
    
    if price_ratio > 1.5:  # If max price is 50%+ higher than min
        cheapest = min(proposals, key=lambda x: x["price"])
        most_expensive = max(proposals, key=lambda x: x["price"])
        red_flags.append(f"Significant price variation: {most_expensive['vendor_name']} costs {price_ratio:.1f}x more than {cheapest['vendor_name']}")
    
    # Scope complexity vs timeline check
    for proposal in proposals:
        scope_length = len(proposal["scope_summary"])
        timeline_months = extract_timeline_months(proposal["delivery_timeline"])
        
        # If very detailed scope but very short timeline
        if scope_length > 500 and timeline_months < 4:
            red_flags.append(f"{proposal['vendor_name']}: Complex scope ({scope_length} chars) with short timeline ({timeline_months:.1f} months)")
    
    return red_flags


def analyze_business_patterns(proposals: List[Dict[str, Any]]) -> List[str]:
    """
    Analyze business patterns and generate insights.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        List of business insights
    """
    insights = []
    
    if not proposals:
        return insights
    
    # Price analysis
    prices = [p["price"] for p in proposals]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    price_spread = max_price - min_price
    
    cheapest = min(proposals, key=lambda x: x["price"])
    most_expensive = max(proposals, key=lambda x: x["price"])
    
    insights.append(f"Price analysis: ${price_spread:,.0f} spread from {cheapest['vendor_name']} (${min_price:,.0f}) to {most_expensive['vendor_name']} (${max_price:,.0f})")
    
    # Timeline analysis
    timelines = [extract_timeline_months(p["delivery_timeline"]) for p in proposals]
    fastest_timeline = min(timelines)
    longest_timeline = max(timelines)
    
    fastest_vendor = min(proposals, key=lambda x: extract_timeline_months(x["delivery_timeline"]))
    
    if fastest_timeline < longest_timeline:
        time_advantage = longest_timeline - fastest_timeline
        insights.append(f"Timeline advantage: {fastest_vendor['vendor_name']} delivers {time_advantage:.1f} months faster than competitors")
    
    # Risk distribution
    risk_levels = [analyze_risk_level(p["risks"]) for p in proposals]
    risk_counts = {
        "Low": risk_levels.count("Low"),
        "Medium": risk_levels.count("Medium"), 
        "High": risk_levels.count("High")
    }
    
    if risk_counts["High"] > 0:
        high_risk_vendors = [p["vendor_name"] for p in proposals if analyze_risk_level(p["risks"]) == "High"]
        insights.append(f"Risk assessment: {len(high_risk_vendors)} high-risk vendors identified: {', '.join(high_risk_vendors)}")
    
    # Value proposition analysis
    value_scores = []
    for proposal in proposals:
        # Simple value score: (max_price - price) / timeline_months
        timeline = extract_timeline_months(proposal["delivery_timeline"])
        price_advantage = max_price - proposal["price"]
        value_score = price_advantage / timeline if timeline > 0 else 0
        value_scores.append((proposal["vendor_name"], value_score))
    
    best_value = max(value_scores, key=lambda x: x[1])
    if best_value[1] > 0:
        insights.append(f"Value proposition: {best_value[0]} offers best price-to-speed ratio")
    
    return insights


def generate_business_recommendation(proposals: List[Dict[str, Any]], 
                                   recommendations: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate executive business recommendation.
    
    Args:
        proposals: List of proposal dictionaries
        recommendations: Recommendation data from weighted analysis
        
    Returns:
        Business recommendation with reasoning
    """
    if not proposals:
        return {"error": "No proposals to analyze"}
    
    # Get balanced recommendation as primary choice
    if recommendations and recommendations.get("recommendations"):
        top_choice = recommendations["recommendations"][0]
        primary_vendor = top_choice["vendor_name"]
        primary_score = top_choice.get("final_score", 0)
    else:
        # Fallback to price-based recommendation
        primary_choice = min(proposals, key=lambda x: x["price"])
        primary_vendor = primary_choice["vendor_name"]
        primary_score = 1.0
    
    # Find alternatives
    alternatives = []
    sorted_proposals = sorted(proposals, key=lambda x: x["price"])
    
    for proposal in sorted_proposals:
        if proposal["vendor_name"] != primary_vendor:
            risk_level = analyze_risk_level(proposal["risks"])
            alternatives.append({
                "vendor": proposal["vendor_name"],
                "reason": f"${proposal['price']:,.0f}, {risk_level.lower()} risk alternative"
            })
    
    # Generate reasoning
    primary_proposal = next(p for p in proposals if p["vendor_name"] == primary_vendor)
    risk_level = analyze_risk_level(primary_proposal["risks"])
    timeline_months = extract_timeline_months(primary_proposal["delivery_timeline"])
    
    reasoning_points = []
    
    # Price reasoning
    prices = [p["price"] for p in proposals]
    price_rank = sorted(prices).index(primary_proposal["price"]) + 1
    if price_rank <= 2:
        reasoning_points.append(f"Competitive pricing (#{price_rank} of {len(proposals)})")
    
    # Timeline reasoning
    timelines = [extract_timeline_months(p["delivery_timeline"]) for p in proposals]
    timeline_rank = sorted(timelines).index(timeline_months) + 1
    if timeline_rank <= 2:
        reasoning_points.append(f"Fast delivery (#{timeline_rank} fastest)")
    
    # Risk reasoning
    if risk_level != "High":
        reasoning_points.append(f"Acceptable risk level ({risk_level.lower()})")
    
    # Score reasoning
    if primary_score > 0.6:
        reasoning_points.append(f"High evaluation score ({primary_score:.3f})")
    
    # Generate next steps
    next_steps = [
        f"Conduct reference checks for {primary_vendor}",
        "Verify technical requirements and capabilities",
        "Negotiate contract terms and pricing"
    ]
    
    # Add specific next steps based on analysis
    red_flags = identify_red_flags(proposals)
    if red_flags:
        next_steps.insert(0, "Address identified red flags before proceeding")
    
    scope_issues = detect_scope_mismatches(proposals)
    if scope_issues:
        next_steps.insert(0, "Clarify scope requirements with all vendors")
    
    return {
        "primary_choice": primary_vendor,
        "confidence_score": primary_score,
        "reasoning": reasoning_points,
        "alternatives": alternatives[:2],  # Top 2 alternatives
        "next_steps": next_steps,
        "decision_factors": {
            "price": f"${primary_proposal['price']:,.0f}",
            "timeline": f"{timeline_months:.1f} months",
            "risk_level": risk_level
        }
    }


def create_vendor_comparison_table(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create executive-friendly vendor comparison table.
    
    Args:
        proposals: List of proposal dictionaries
        
    Returns:
        Formatted comparison table for business presentation
    """
    if not proposals:
        return []
    
    comparison_table = []
    
    for proposal in proposals:
        timeline_months = extract_timeline_months(proposal["delivery_timeline"])
        risk_level = analyze_risk_level(proposal["risks"])
        
        # Determine scope alignment
        scope_text = proposal["scope_summary"].lower()
        if "portal" in scope_text or "management" in scope_text:
            scope_alignment = "Perfect"
        elif "ai" in scope_text or "machine learning" in scope_text:
            scope_alignment = "Unclear"
        else:
            scope_alignment = "Review"
        
        comparison_table.append({
            "vendor": proposal["vendor_name"],
            "project_type": proposal["project_name"],
            "price": f"${proposal['price']:,.0f}",
            "timeline": f"{timeline_months:.1f} months",
            "risk_level": risk_level,
            "scope_alignment": scope_alignment,
            "price_rank": "#" + str(sorted([p["price"] for p in proposals]).index(proposal["price"]) + 1)
        })
    
    # Sort by price for presentation
    comparison_table.sort(key=lambda x: int(x["price_rank"].replace("#", "")))
    
    return comparison_table


def generate_executive_summary_report(proposals: List[Dict[str, Any]], 
                                    comparison_report: Dict[str, Any] = None,
                                    recommendations: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate comprehensive executive summary report.
    
    Args:
        proposals: List of proposal dictionaries
        comparison_report: Existing comparison report data
        recommendations: Recommendation data
        
    Returns:
        Executive summary report with business insights
    """
    print("Generating executive business analysis report...")
    
    if not proposals:
        return {"error": "No proposals to analyze"}
    
    # Generate all analysis components
    vendor_table = create_vendor_comparison_table(proposals)
    scope_issues = detect_scope_mismatches(proposals)
    red_flags = identify_red_flags(proposals, recommendations)
    business_insights = analyze_business_patterns(proposals)
    business_recommendation = generate_business_recommendation(proposals, recommendations)
    
    # Create executive summary
    total_vendors = len(proposals)
    price_range = f"${min(p['price'] for p in proposals):,.0f} - ${max(p['price'] for p in proposals):,.0f}"
    
    executive_summary = {
        "overview": f"Evaluated {total_vendors} vendor proposals with price range {price_range}",
        "key_finding": f"Recommended vendor: {business_recommendation['primary_choice']}",
        "critical_issues": len(scope_issues) + len(red_flags),
        "decision_confidence": business_recommendation.get("confidence_score", 0)
    }
    
    # Compile full report
    report = {
        "report_metadata": {
            "report_type": "executive_business_analysis",
            "generated_at": datetime.now().isoformat(),
            "total_vendors_analyzed": total_vendors
        },
        "executive_summary": executive_summary,
        "vendor_comparison_table": vendor_table,
        "key_issues_identified": scope_issues + red_flags,
        "business_insights": business_insights,
        "business_recommendation": business_recommendation,
        "raw_data_references": {
            "comparison_report": comparison_report.get("report_metadata", {}).get("generated_at") if comparison_report else None,
            "recommendation_data": recommendations.get("evaluation_metadata", {}).get("generated_at") if recommendations else None
        }
    }
    
    return report


def save_executive_summary_report(executive_report: Dict[str, Any], output_dir: str = "outputs") -> str:
    """
    Save executive summary report to JSON file.
    
    Args:
        executive_report: Complete executive report
        output_dir: Output directory
        
    Returns:
        Path to saved report file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f"executive_summary_{timestamp}.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(executive_report, f, indent=2, ensure_ascii=False)
    
    return report_path


def display_executive_summary(executive_report: Dict[str, Any]):
    """
    Display simplified executive summary for capstone demo.
    
    Args:
        executive_report: Executive summary report data
    """
    if executive_report.get("error"):
        print(f"Error: {executive_report['error']}")
        return
    
    print("\n" + "="*60)
    print("AI PROCUREMENT AGENT - VENDOR ANALYSIS")
    print("="*60)
    
    # Simple overview
    summary = executive_report["executive_summary"]
    print(f"\nANALYSIS SUMMARY:")
    print(f"   {summary['overview']}")
    print(f"   {summary['key_finding']}")
    
    # Vendor comparison table
    print(f"\nVENDOR COMPARISON:")
    table = executive_report["vendor_comparison_table"]
    if table:
        print(f"   {'Vendor':<20} {'Price':<12} {'Timeline':<12} {'Risk':<10}")
        print(f"   {'-'*20} {'-'*12} {'-'*12} {'-'*10}")
        for row in table:
            print(f"   {row['vendor']:<20} {row['price']:<12} {row['timeline']:<12} {row['risk_level']:<10}")
    
    # Recommendation
    rec = executive_report["business_recommendation"]
    print(f"\nAI RECOMMENDATION:")
    print(f"   Top Choice: {rec['primary_choice']}")
    
    factors = rec.get("decision_factors", {})
    print(f"   Key Factors: ${factors.get('price', 'N/A')} | {factors.get('timeline', 'N/A')} | {factors.get('risk_level', 'N/A')} risk")
    
    if rec.get("reasoning"):
        top_reasons = rec['reasoning'][:2]  # Just top 2 reasons
        print(f"   Why: {', '.join(top_reasons)}")
    
    print("\n" + "="*60) 