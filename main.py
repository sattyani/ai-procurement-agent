"""
AI Procurement Agent - Main Entry Point
Complete pipeline for RFP analysis and vendor proposal evaluation
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our analysis modules
from rfp_analyzer import analyze_smart_parking_rfp
from vendor_analyzer import analyze_vendor_proposals
from evaluation_engine import evaluate_all_vendors

def print_header():
    """Print application header"""
    print("=" * 80)
    print("AI PROCUREMENT AGENT")
    print("Automated RFP Analysis & Vendor Proposal Evaluation")
    print("=" * 80)

def check_prerequisites() -> bool:
    """Check if all prerequisites are met"""
    print("\nChecking Prerequisites...")
    print("-" * 40)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found")
        print("Please set your OpenAI API key as an environment variable")
        return False
    print("✓ OpenAI API key found")
    
    # Check required directories
    required_dirs = ["data", "data/proposals"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"ERROR: Required directory '{directory}' not found")
            return False
        print(f"✓ Directory '{directory}' exists")
    
    # Check for RFP file
    rfp_file = "data/smart_parking_rfp.pdf"
    if not os.path.exists(rfp_file):
        print(f"ERROR: RFP file '{rfp_file}' not found")
        return False
    print(f"✓ RFP file found: {rfp_file}")
    
    # Check for vendor proposals
    import glob
    proposals = glob.glob("data/proposals/*.pdf")
    if not proposals:
        print("ERROR: No vendor proposal PDFs found in data/proposals/")
        return False
    print(f"✓ Found {len(proposals)} vendor proposals")
    
    return True

def ensure_output_directories():
    """Ensure output directories exist"""
    output_dirs = [
        "outputs",
        "outputs/rfp_analysis", 
        "outputs/proposal_analysis",
        "outputs/reports"
    ]
    
    for directory in output_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)

def step1_rfp_analysis() -> bool:
    """Step 1: Analyze RFP and extract requirements"""
    print("\n" + "=" * 80)
    print("STEP 1: RFP ANALYSIS")
    print("=" * 80)
    print("Extracting structured requirements from RFP document...")
    
    try:
        result = analyze_smart_parking_rfp()
        if result:
            print("\n✓ Step 1 COMPLETED: RFP analysis successful")
            print(f"  RFP requirements extracted and saved")
            return True
        else:
            print("\n✗ Step 1 FAILED: Could not analyze RFP")
            return False
    except Exception as e:
        print(f"\n✗ Step 1 FAILED: {e}")
        return False

def step2_vendor_analysis() -> Dict[str, Any]:
    """Step 2: Analyze all vendor proposals"""
    print("\n" + "=" * 80)
    print("STEP 2: VENDOR PROPOSAL ANALYSIS")
    print("=" * 80)
    print("Processing all vendor proposals against RFP requirements...")
    
    try:
        results = analyze_vendor_proposals()
        if results:
            print(f"\n✓ Step 2 COMPLETED: Analyzed {len(results)} vendor proposals")
            return results
        else:
            print("\n✗ Step 2 FAILED: No vendor proposals processed")
            return {}
    except Exception as e:
        print(f"\n✗ Step 2 FAILED: {e}")
        return {}

def step3_generate_final_report(vendor_results: Dict[str, Any]):
    """Step 3: Advanced evaluation and final procurement recommendation"""
    print("\n" + "=" * 80)
    print("STEP 3: ADVANCED EVALUATION & FINAL REPORT")
    print("=" * 80)
    
    if not vendor_results:
        print("No vendor data available for evaluation")
        return
    
    # Run advanced AI evaluation
    print("Running AI-powered evaluation across all criteria...")
    vendor_evaluations = evaluate_all_vendors(
        rfp_json_path="outputs/rfp_analysis/smart_parking_extracted.json",
        vendor_analyses=vendor_results
    )
    
    if not vendor_evaluations:
        print("Advanced evaluation failed, falling back to basic analysis")
        return
    
    # Save detailed evaluations
    evaluations_dir = "outputs/evaluations"
    Path(evaluations_dir).mkdir(parents=True, exist_ok=True)
    
    for evaluation in vendor_evaluations:
        vendor_name = evaluation['vendor_name'].replace(' ', '_').lower()
        eval_path = f"{evaluations_dir}/{vendor_name}_detailed_evaluation.json"
        with open(eval_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
    
    # Generate executive summary
    print("\n" + "=" * 80)
    print("EXECUTIVE PROCUREMENT RECOMMENDATION")
    print("=" * 80)
    
    top_3_vendors = vendor_evaluations[:3]
    
    print(f"Total Proposals Evaluated: {len(vendor_evaluations)}")
    print(f"Evaluation Criteria: {len(vendor_evaluations[0]['criteria_scores'])} dimensions")
    
    print(f"\nTOP 3 RECOMMENDED VENDORS:")
    print("-" * 50)
    
    for i, vendor in enumerate(top_3_vendors, 1):
        score = vendor['total_weighted_score']
        confidence = vendor['overall_confidence']
        recommendation = vendor['evaluation_summary']['recommendation']
        
        print(f"{i}. {vendor['vendor_name']}")
        print(f"   Score: {score:.2f}/10 (Confidence: {confidence})")
        print(f"   Status: {recommendation}")
        
        # Show top strengths
        strengths = vendor['evaluation_summary']['strengths'][:2]
        if strengths:
            print(f"   Key Strengths:")
            for strength in strengths:
                print(f"     • {strength}")
        print()
    
    # Detailed analysis of top vendor
    best_vendor = vendor_evaluations[0]
    print(f"RECOMMENDED VENDOR: {best_vendor['vendor_name']}")
    print("-" * 50)
    print(f"Overall Score: {best_vendor['total_weighted_score']:.2f}/10")
    print(f"Confidence Level: {best_vendor['overall_confidence']}")
    
    print(f"\nDetailed Scores:")
    for criteria, data in best_vendor['criteria_scores'].items():
        score = data['raw_score']
        weight = data['weight']
        weighted = data['weighted_score']
        print(f"  {criteria}: {score}/10 (Weight: {weight:.1%}) = {weighted:.2f}")
    
    # Generate advanced comparison analysis
    from evaluation_engine import AdvancedReportGenerator
    advanced_reporter = AdvancedReportGenerator(
        rfp_data={"evaluation_criteria": vendor_evaluations[0]['criteria_scores']}
    )
    
    # Generate comprehensive reports with advanced analytics
    advanced_analysis = advanced_reporter.generate_advanced_comparison_report(vendor_evaluations)
    
    # Save executive summary report
    report_path = "outputs/reports/executive_procurement_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("EXECUTIVE PROCUREMENT EVALUATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Project: Smart Parking System Implementation\n")
        f.write(f"Total Vendors Evaluated: {len(vendor_evaluations)}\n")
        f.write(f"Evaluation Date: {Path().cwd()}\n\n")
        
        f.write("RANKING SUMMARY:\n")
        f.write("-" * 30 + "\n")
        for i, vendor in enumerate(vendor_evaluations, 1):
            f.write(f"{i}. {vendor['vendor_name']} - Score: {vendor['total_weighted_score']:.2f}/10\n")
        
        f.write(f"\nRECOMMENDED VENDOR:\n")
        f.write(f"Company: {best_vendor['vendor_name']}\n")
        f.write(f"Overall Score: {best_vendor['total_weighted_score']:.2f}/10\n")
        f.write(f"Confidence: {best_vendor['overall_confidence']}\n")
        f.write(f"Recommendation: {best_vendor['evaluation_summary']['recommendation']}\n\n")
        
        f.write("DETAILED EVALUATION CRITERIA:\n")
        f.write("-" * 40 + "\n")
        for criteria, data in best_vendor['criteria_scores'].items():
            f.write(f"{criteria}: {data['raw_score']}/10 (Weight: {data['weight']:.1%})\n")
            f.write(f"  Justification: {data['justification'][:200]}...\n\n")
    
    # Save comprehensive advanced analysis report
    advanced_report_path = "outputs/reports/advanced_comparison_analysis.txt"
    with open(advanced_report_path, 'w', encoding='utf-8') as f:
        f.write("ADVANCED VENDOR COMPARISON & ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Project: Smart Parking System Implementation\n")
        f.write(f"Generated by AI Procurement Agent\n\n")
        f.write(advanced_analysis)
    
    # Save vendor comparison matrix as CSV for spreadsheet analysis
    matrix_csv_path = "outputs/reports/vendor_comparison_matrix.csv"
    with open(matrix_csv_path, 'w', encoding='utf-8') as f:
        if vendor_evaluations:
            criteria_names = list(vendor_evaluations[0]['criteria_scores'].keys())
            
            # CSV header
            header = "Vendor,Rank,Total Score,Confidence"
            for criteria in criteria_names:
                header += f",{criteria}_Score,{criteria}_Weight"
            f.write(header + "\n")
            
            # CSV data rows
            for vendor in vendor_evaluations:
                row = f"{vendor['vendor_name']},{vendor['rank']},{vendor['total_weighted_score']:.2f},{vendor['overall_confidence']}"
                for criteria in criteria_names:
                    score = vendor['criteria_scores'][criteria]['raw_score']
                    weight = vendor['criteria_scores'][criteria]['weight']
                    row += f",{score},{weight:.2f}"
                f.write(row + "\n")
    
    print(f"\n✓ Step 3 COMPLETED: Advanced evaluation and reporting complete")
    print(f"✓ Executive summary: {report_path}")
    print(f"✓ Advanced analytics: {advanced_report_path}")
    print(f"✓ Comparison matrix: {matrix_csv_path}")
    print(f"✓ Detailed evaluations: {evaluations_dir}/")
    
    return vendor_evaluations

def main():
    """Main execution pipeline"""
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nExiting due to missing prerequisites")
        sys.exit(1)
    
    # Ensure output directories exist
    ensure_output_directories()
    
    # Step 1: RFP Analysis
    if not step1_rfp_analysis():
        print("\nExiting due to RFP analysis failure")
        sys.exit(1)
    
    # Step 2: Vendor Analysis
    vendor_results = step2_vendor_analysis()
    if not vendor_results:
        print("\nExiting due to vendor analysis failure")
        sys.exit(1)
    
    # Step 3: Final Report
    step3_generate_final_report(vendor_results)
    
    # Success summary
    print("\n" + "=" * 80)
    print("PROCUREMENT ANALYSIS COMPLETE")
    print("=" * 80)
    print("✓ RFP requirements extracted")
    print(f"✓ {len(vendor_results)} vendor proposals analyzed")
    print("✓ Procurement recommendation generated")
    print("\nFiles Generated:")
    print("  - outputs/rfp_analysis/smart_parking_extracted.json")
    print("  - outputs/proposal_analysis/*_analysis.json")
    print("  - outputs/evaluations/*_detailed_evaluation.json")
    print("  - outputs/reports/executive_procurement_report.txt")
    print("  - outputs/reports/advanced_comparison_analysis.txt")
    print("  - outputs/reports/vendor_comparison_matrix.csv")
    print("\nAdvanced AI evaluation complete - ready for procurement decision!")

if __name__ == "__main__":
    main() 