"""
Simple RFP Schema for Capstone Project
Basic structure for AI-extracted RFP data
"""

import json
from typing import Dict, List, Any

# Simple RFP template structure
RFP_TEMPLATE = {
    "project_code": "",
    "project_name": "",
    "issuing_authority": "",
    "timeline_days": 0,
    "budget_sar": 0,
    "required_scope": [],
    "evaluation_criteria": {},
    "mandatory_requirements": []
}

# Required fields for basic validation
REQUIRED_FIELDS = [
    "project_code",
    "project_name", 
    "timeline_days",
    "required_scope",
    "evaluation_criteria"
]

def create_empty_rfp():
    """Create empty RFP structure"""
    return RFP_TEMPLATE.copy()

def validate_rfp(rfp_data):
    """
    Simple validation of RFP data
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in rfp_data or not rfp_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Check evaluation criteria weights sum to 1.0
    if "evaluation_criteria" in rfp_data and rfp_data["evaluation_criteria"]:
        weights = rfp_data["evaluation_criteria"]
        if isinstance(weights, dict):
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                errors.append(f"Evaluation weights must sum to 1.0, got {total:.2f}")
    
    return len(errors) == 0, errors

def save_rfp(rfp_data, filename):
    """Save RFP data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(rfp_data, f, indent=2)
        print(f"RFP saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving RFP: {e}")
        return False

def load_rfp(filename):
    """Load RFP data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading RFP: {e}")
        return None

def print_rfp_summary(rfp_data):
    """Print simple RFP summary"""
    print("=" * 50)
    print("RFP SUMMARY")
    print("=" * 50)
    print(f"Project: {rfp_data.get('project_code', 'N/A')}")
    print(f"Name: {rfp_data.get('project_name', 'N/A')}")
    print(f"Authority: {rfp_data.get('issuing_authority', 'N/A')}")
    print(f"Timeline: {rfp_data.get('timeline_days', 0)} days")
    print(f"Budget: {rfp_data.get('budget_sar', 0):,} SAR")
    
    scope = rfp_data.get('required_scope', [])
    print(f"\nScope ({len(scope)} items):")
    for i, item in enumerate(scope, 1):
        print(f"   {i}. {item}")
    
    criteria = rfp_data.get('evaluation_criteria', {})
    if criteria:
        print(f"\nEvaluation Criteria:")
        for name, weight in criteria.items():
            print(f"   {name}: {weight:.1%}")
    
    requirements = rfp_data.get('mandatory_requirements', [])
    if requirements:
        print(f"\nMandatory Requirements ({len(requirements)}):")
        for req in requirements:
            print(f"   - {req}")
    
    print("=" * 50)

if __name__ == "__main__":
    # Test the simple schema
    print("Testing Simple RFP Schema...")
    
    # Create and test empty RFP
    rfp = create_empty_rfp()
    is_valid, errors = validate_rfp(rfp)
    
    print(f"Empty RFP validation: {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        for error in errors:
            print(f"   - {error}")
    
    # Test with sample data
    sample_rfp = {
        "project_code": "TEST-001",
        "project_name": "Sample Project",
        "issuing_authority": "Test Authority",
        "timeline_days": 90,
        "budget_sar": 100000,
        "required_scope": ["Requirement 1", "Requirement 2"],
        "evaluation_criteria": {
            "technical": 0.4,
            "cost": 0.3,
            "timeline": 0.3
        },
        "mandatory_requirements": ["Must have certification"]
    }
    
    is_valid, errors = validate_rfp(sample_rfp)
    print(f"\nSample RFP validation: {'PASSED' if is_valid else 'FAILED'}")
    
    if is_valid:
        print_rfp_summary(sample_rfp) 