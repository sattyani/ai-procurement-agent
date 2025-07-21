"""
Vendor Proposal Analyzer
Processes vendor PDF proposals against RFP requirements using AI extraction
"""

import os
import glob
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from rfp_schema import load_rfp

class VendorAnalyzer:
    """Analyzes vendor proposals against RFP requirements"""
    
    def __init__(self, rfp_path: str, proposals_folder: str = "data/proposals", 
                 output_folder: str = "outputs/proposal_analysis"):
        """
        Initialize vendor analyzer
        
        Args:
            rfp_path: Path to extracted RFP JSON file
            proposals_folder: Folder containing vendor PDF proposals
            output_folder: Folder to save analysis results
        """
        self.rfp_path = rfp_path
        self.proposals_folder = proposals_folder
        self.output_folder = output_folder
        self.rfp_data = None
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=3000)
        
        # Ensure output directory exists
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
    
    def load_rfp_requirements(self) -> bool:
        """Load RFP requirements for analysis"""
        self.rfp_data = load_rfp(self.rfp_path)
        if not self.rfp_data:
            print(f"Error: Could not load RFP data from {self.rfp_path}")
            return False
        return True
    
    def get_proposal_files(self) -> List[str]:
        """Get list of PDF proposal files"""
        pattern = os.path.join(self.proposals_folder, "*.pdf")
        files = glob.glob(pattern)
        return sorted(files)
    
    def extract_vendor_name_from_filename(self, filepath: str) -> str:
        """Extract vendor name from filename"""
        filename = os.path.basename(filepath)
        # Remove .pdf extension and clean up
        name = filename.replace('.pdf', '')
        # Handle different naming patterns
        if 'proposal' in name.lower():
            name = name.replace('_proposal', '').replace(' proposal', '')
            name = name.replace('Proposal', '').replace('_Proposal', '')
        return name.replace('_', ' ').strip()
    
    def load_proposal_content(self, pdf_path: str) -> Optional[str]:
        """Load content from vendor proposal PDF"""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            content = "\n\n".join([doc.page_content for doc in documents])
            return content
        except Exception as e:
            print(f"Error loading PDF {pdf_path}: {e}")
            return None
    
    def extract_vendor_data(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from vendor proposal"""
        
        if not self.rfp_data:
            print("Error: RFP data not loaded")
            return None
        
        # Load proposal content
        content = self.load_proposal_content(pdf_path)
        if not content:
            return None
        
        # Create extraction prompt
        prompt = f"""
        You are analyzing a vendor proposal against specific RFP requirements.

        RFP REQUIREMENTS TO CHECK:
        - Timeline Limit: {self.rfp_data.get('timeline_days')} days maximum
        - Budget Limit: {self.rfp_data.get('budget_sar'):,} SAR maximum
        - Required Scope: {self.rfp_data.get('required_scope')}
        - Mandatory Requirements: {self.rfp_data.get('mandatory_requirements')}

        VENDOR PROPOSAL CONTENT:
        {content}

        Extract the vendor's responses to each RFP requirement. If information is missing or unclear, indicate this clearly.

        Return ONLY a valid JSON object with this structure:
        {{
            "vendor_name": "Company name",
            "contact_person": "Contact details if available",
            "extraction_confidence": "high|medium|low",
            "rfp_responses": {{
                "timeline_proposed_days": "number or 'not specified'",
                "budget_proposed_sar": "number or 'not specified'",
                "scope_coverage": {{
                    // For each RFP scope item, vendor's response or "not mentioned"
                }},
                "compliance_status": {{
                    // For each mandatory requirement, vendor's status or "not mentioned"
                }},
                "missing_information": ["list of critical information not found"],
                "additional_offerings": ["list of extra services/guarantees"]
            }}
        }}
        """
        
        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            # Clean response
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {pdf_path}: {e}")
            return None
        except Exception as e:
            print(f"Extraction error for {pdf_path}: {e}")
            return None
    
    def save_analysis_result(self, vendor_data: Dict[str, Any], original_filename: str) -> str:
        """Save vendor analysis to JSON file"""
        # Create safe filename
        base_name = os.path.basename(original_filename).replace('.pdf', '')
        safe_name = base_name.replace(' ', '_').replace('(', '').replace(')', '').lower()
        output_path = os.path.join(self.output_folder, f"{safe_name}_analysis.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vendor_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def process_single_proposal(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """Process a single vendor proposal"""
        filename = os.path.basename(pdf_path)
        print(f"\nProcessing: {filename}")
        print("-" * 50)
        
        # Extract data
        vendor_data = self.extract_vendor_data(pdf_path)
        if not vendor_data:
            print(f"  Status: Failed to extract data")
            return None
        
        # Save result
        output_path = self.save_analysis_result(vendor_data, pdf_path)
        print(f"  Status: Analysis completed")
        print(f"  Saved to: {os.path.basename(output_path)}")
        
        return vendor_data
    
    def process_all_proposals(self) -> Dict[str, Any]:
        """Process all vendor proposals in the folder"""
        
        print("VENDOR PROPOSAL ANALYSIS")
        print("=" * 60)
        
        # Load RFP requirements
        if not self.load_rfp_requirements():
            return {}
        
        # Get proposal files
        proposal_files = self.get_proposal_files()
        if not proposal_files:
            print(f"No PDF files found in {self.proposals_folder}")
            return {}
        
        print(f"Found {len(proposal_files)} proposals to process")
        
        results = {}
        
        # Process each proposal
        for pdf_path in proposal_files:
            vendor_data = self.process_single_proposal(pdf_path)
            if vendor_data:
                results[pdf_path] = vendor_data
        
        print(f"\nProcessed {len(results)} proposals successfully")
        return results
    
    def generate_comparison_report(self, results: Dict[str, Any]) -> None:
        """Generate comparison report of all vendors"""
        
        if not results:
            print("No results to compare")
            return
        
        print("\n" + "=" * 80)
        print("VENDOR COMPARISON REPORT")
        print("=" * 80)
        
        # Create comparison table
        headers = ["Vendor", "Budget", "Timeline", "Scope Coverage", "Compliance", "Confidence"]
        print(f"{headers[0]:<25} | {headers[1]:<12} | {headers[2]:<10} | {headers[3]:<15} | {headers[4]:<10} | {headers[5]:<10}")
        print("-" * 95)
        
        for pdf_path, vendor_data in results.items():
            vendor_name = vendor_data.get('vendor_name', 'Unknown')[:24]
            confidence = vendor_data.get('extraction_confidence', 'unknown')
            rfp_responses = vendor_data.get('rfp_responses', {})
            
            # Budget
            budget = rfp_responses.get('budget_proposed_sar')
            budget_str = f"{budget:,}" if isinstance(budget, (int, float)) else "Not Found"
            
            # Timeline
            timeline = rfp_responses.get('timeline_proposed_days')
            timeline_str = f"{timeline}d" if isinstance(timeline, (int, float)) else "Not Found"
            
            # Scope coverage
            scope_coverage = rfp_responses.get('scope_coverage', {})
            if scope_coverage:
                covered = sum(1 for v in scope_coverage.values() 
                            if v.lower() not in ['not mentioned', 'not specified', 'unclear'])
                scope_str = f"{covered}/{len(scope_coverage)}"
            else:
                scope_str = "0/0"
            
            # Compliance
            compliance_status = rfp_responses.get('compliance_status', {})
            if compliance_status:
                compliant = sum(1 for v in compliance_status.values() 
                              if v.lower() not in ['not mentioned', 'not specified', 'unclear'])
                compliance_str = f"{compliant}/{len(compliance_status)}"
            else:
                compliance_str = "0/0"
            
            print(f"{vendor_name:<25} | {budget_str:<12} | {timeline_str:<10} | {scope_str:<15} | {compliance_str:<10} | {confidence:<10}")

def analyze_vendor_proposals(rfp_json_path: str = "outputs/rfp_analysis/smart_parking_extracted.json",
                           proposals_folder: str = "data/proposals") -> Dict[str, Any]:
    """
    Main function to analyze all vendor proposals
    
    Args:
        rfp_json_path: Path to extracted RFP JSON
        proposals_folder: Folder containing vendor proposals
        
    Returns:
        Dictionary of analysis results
    """
    analyzer = VendorAnalyzer(rfp_json_path, proposals_folder)
    results = analyzer.process_all_proposals()
    analyzer.generate_comparison_report(results)
    return results

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        print("Please set your OpenAI API key")
    else:
        analyze_vendor_proposals() 