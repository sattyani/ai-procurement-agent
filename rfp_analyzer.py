"""
AI-Powered RFP Analyzer
Reads RFP PDFs and extracts structured data using GPT-4o
"""

import os
from typing import Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json
from rfp_schema import RFP_TEMPLATE, validate_rfp, save_rfp, print_rfp_summary

class RFPAnalyzer:
    """AI-powered RFP analyzer using GPT-4o"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the RFP analyzer
        
        Args:
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass as parameter.")
        
        # Initialize GPT-4o model
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=2000
        )
    
    def load_pdf(self, pdf_path: str) -> str:
        """
        Load and extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Combine all pages into single text
            full_text = "\n\n".join([doc.page_content for doc in documents])
            
            print(f"Loaded PDF: {pdf_path}")
            print(f"Pages: {len(documents)}")
            print(f"Text length: {len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return ""
    
    def extract_rfp_data(self, rfp_text: str) -> Dict[str, Any]:
        """
        Extract structured RFP data using AI
        
        Args:
            rfp_text: Raw RFP text content
            
        Returns:
            Dictionary with extracted RFP data
        """
        # Create extraction prompt
        extraction_prompt = f"""
You are an AI assistant that extracts structured data from RFP (Request for Proposal) documents.

Please analyze the following RFP text and extract the key information into a JSON structure.

Extract these specific fields:
1. project_code: The project identifier/code
2. project_name: The name/title of the project
3. issuing_authority: The organization issuing the RFP
4. timeline_days: Project duration/deadline in days (convert any time periods to days)
5. budget_sar: Maximum budget amount in SAR (extract number only, convert if needed)
6. required_scope: List of main deliverables/requirements (5-10 key items)
7. evaluation_criteria: Dictionary with criteria names and weights (weights must sum to 1.0)
8. mandatory_requirements: List of mandatory/compliance requirements

Important guidelines:
- Extract exact values when possible
- If timeline is in weeks/months, convert to days (1 month = 30 days, 1 week = 7 days)
- For evaluation criteria, ensure weights are decimal values that sum to 1.0
- Focus on the most important scope items and requirements
- If a field is not found, use appropriate defaults (empty string, 0, empty list)

RFP TEXT:
{rfp_text}

Return ONLY a valid JSON object with the extracted data:
"""

        try:
            # Send to GPT-4o for extraction
            message = HumanMessage(content=extraction_prompt)
            response = self.llm.invoke([message])
            
            # Clean the response (remove markdown formatting if present)
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Parse the JSON response
            extracted_data = json.loads(response_text)
            
            print("AI extraction completed")
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            print(f"Raw response: {response.content}")
            return RFP_TEMPLATE.copy()
            
        except Exception as e:
            print(f"Error during AI extraction: {e}")
            return RFP_TEMPLATE.copy()
    
    def analyze_rfp(self, pdf_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete RFP analysis pipeline: PDF → AI extraction → validation
        
        Args:
            pdf_path: Path to RFP PDF file
            output_path: Optional path to save extracted JSON
            
        Returns:
            Dictionary with extracted and validated RFP data
        """
        print("=" * 60)
        print("AI RFP ANALYZER")
        print("=" * 60)
        
        # Ensure output directory exists
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
        
        # Step 1: Load PDF
        print("\nStep 1: Loading PDF...")
        rfp_text = self.load_pdf(pdf_path)
        
        if not rfp_text:
            print("Failed to load PDF content")
            return RFP_TEMPLATE.copy()
        
        # Step 2: AI extraction
        print("\nStep 2: AI extraction...")
        extracted_data = self.extract_rfp_data(rfp_text)
        
        # Step 3: Validation
        print("\nStep 3: Validation...")
        is_valid, errors = validate_rfp(extracted_data)
        
        if is_valid:
            print("Validation: PASSED")
        else:
            print("Validation: FAILED")
            for error in errors:
                print(f"   - {error}")
        
        # Step 4: Save if requested
        if output_path:
            print(f"\nStep 4: Saving to {output_path}...")
            save_rfp(extracted_data, output_path)
        
        # Step 5: Display summary
        print("\nStep 5: Extracted RFP Summary:")
        print_rfp_summary(extracted_data)
        
        return extracted_data

def analyze_smart_parking_rfp():
    """Convenience function to analyze the Smart Parking RFP"""
    try:
        analyzer = RFPAnalyzer()
        result = analyzer.analyze_rfp(
            pdf_path="data/smart_parking_rfp.pdf",
            output_path="outputs/rfp_analysis/smart_parking_extracted.json"
        )
        return result
    except Exception as e:
        print(f"Error analyzing Smart Parking RFP: {e}")
        return None

if __name__ == "__main__":
    # Test with Smart Parking RFP
    print("Testing AI RFP Analyzer with Smart Parking RFP...")
    
    # Check if PDF exists
    pdf_path = "data/smart_parking_rfp.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        print("Please ensure the Smart Parking RFP PDF exists in the data folder.")
    else:
        result = analyze_smart_parking_rfp()
        if result:
            print("\nAnalysis completed successfully!")
        else:
            print("\nAnalysis failed!") 