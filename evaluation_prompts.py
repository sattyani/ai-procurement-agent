"""
AI Evaluation Prompts for Vendor Scoring
Provides structured prompts for scoring vendors on evaluation criteria (1-10 scale)
"""

from typing import Dict, Any, List

def get_scoring_scale_definition() -> str:
    """Standard 1-10 scoring scale used across all criteria"""
    return """
SCORING SCALE (1-10):
1-2: Poor - Major deficiencies, unacceptable quality
3-4: Below Average - Significant gaps, minimal competence  
5-6: Average - Meets basic requirements, standard quality
7-8: Good - Exceeds requirements, strong competence
9-10: Excellent - Outstanding quality, exceptional capability
"""

def get_technical_capability_prompt(vendor_content: str, rfp_scope: List[str]) -> str:
    """Prompt for evaluating technical capability"""
    scope_items = "\n".join([f"- {item}" for item in rfp_scope])
    
    return f"""
You are evaluating a vendor's TECHNICAL CAPABILITY for a procurement project.

{get_scoring_scale_definition()}

RFP REQUIRED SCOPE:
{scope_items}

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate the vendor's technical capability based on:
1. Demonstrated expertise in required technologies
2. Technical approach and methodology quality
3. Architecture and design competence  
4. Innovation and technical solutions
5. Team qualifications and certifications
6. Previous project complexity and success
7. Technical infrastructure and tools

Provide a score from 1-10 and detailed justification.

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed explanation referencing specific vendor content",
    "strengths": ["List of technical strengths found"],
    "weaknesses": ["List of technical gaps or concerns"],
    "confidence": "high|medium|low"
}}
"""

def get_cost_effectiveness_prompt(vendor_content: str, budget_limit: float, vendor_budget: Any) -> str:
    """Prompt for evaluating cost effectiveness"""
    
    return f"""
You are evaluating a vendor's COST EFFECTIVENESS for a procurement project.

{get_scoring_scale_definition()}

BUDGET CONTEXT:
- RFP Budget Limit: {budget_limit:,} SAR
- Vendor Proposed Budget: {vendor_budget}

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate cost effectiveness based on:
1. Budget competitiveness vs. market rates
2. Value for money proposition
3. Cost breakdown transparency and detail
4. Hidden costs or additional fees
5. Payment terms and financial structure
6. Cost optimization strategies proposed
7. Long-term cost implications

Consider both the absolute cost and the value delivered for that cost.

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed explanation of cost evaluation",
    "strengths": ["Cost-related advantages"],
    "weaknesses": ["Cost concerns or gaps"],
    "confidence": "high|medium|low"
}}
"""

def get_timeline_feasibility_prompt(vendor_content: str, timeline_limit: int, vendor_timeline: Any) -> str:
    """Prompt for evaluating timeline feasibility"""
    
    return f"""
You are evaluating a vendor's TIMELINE FEASIBILITY for a procurement project.

{get_scoring_scale_definition()}

TIMELINE CONTEXT:
- RFP Timeline Limit: {timeline_limit} days maximum
- Vendor Proposed Timeline: {vendor_timeline}

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate timeline feasibility based on:
1. Realistic project scheduling and milestones
2. Resource allocation and availability
3. Parallel vs. sequential work planning
4. Risk buffer and contingency planning
5. Track record of on-time delivery
6. Project management methodology
7. Critical path analysis and dependencies

Consider both the proposed timeline and the quality of planning.

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed timeline evaluation explanation",
    "strengths": ["Timeline planning advantages"],
    "weaknesses": ["Timeline risks or concerns"],
    "confidence": "high|medium|low"
}}
"""

def get_company_experience_prompt(vendor_content: str, project_type: str) -> str:
    """Prompt for evaluating company experience"""
    
    return f"""
You are evaluating a vendor's COMPANY EXPERIENCE for a procurement project.

{get_scoring_scale_definition()}

PROJECT TYPE: {project_type}

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate company experience based on:
1. Years in business and industry presence
2. Similar project experience and case studies
3. Client references and testimonials
4. Industry certifications and accreditations
5. Awards and recognition
6. Financial stability and company size
7. Geographic presence and local expertise

Focus on relevant experience for this specific project type.

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed experience evaluation",
    "strengths": ["Experience-related advantages"],
    "weaknesses": ["Experience gaps or concerns"],
    "confidence": "high|medium|low"
}}
"""

def get_support_prompt(vendor_content: str, mandatory_requirements: List[str]) -> str:
    """Prompt for evaluating post-deployment support"""
    
    requirements = "\n".join([f"- {req}" for req in mandatory_requirements])
    
    return f"""
You are evaluating a vendor's POST-DEPLOYMENT SUPPORT capability.

{get_scoring_scale_definition()}

MANDATORY SUPPORT REQUIREMENTS:
{requirements}

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate support capability based on:
1. Support team size and availability (24/7, business hours)
2. Response time commitments and SLAs
3. Support channels (phone, email, chat, on-site)
4. Escalation procedures and issue resolution
5. Maintenance and update procedures
6. Training and documentation quality
7. Long-term support commitment and pricing

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed support evaluation",
    "strengths": ["Support advantages"],
    "weaknesses": ["Support limitations or gaps"],
    "confidence": "high|medium|low"
}}
"""

def get_evaluation_prompt_for_criteria(criteria_name: str, vendor_content: str, 
                                     rfp_data: Dict[str, Any], vendor_data: Dict[str, Any]) -> str:
    """
    Get the appropriate evaluation prompt based on criteria name
    
    Args:
        criteria_name: Name of evaluation criteria
        vendor_content: Full vendor proposal text
        rfp_data: Extracted RFP data
        vendor_data: Extracted vendor data
        
    Returns:
        Formatted prompt for AI evaluation
    """
    
    # Normalize criteria name for matching
    criteria_lower = criteria_name.lower()
    
    if "technical" in criteria_lower or "capability" in criteria_lower:
        return get_technical_capability_prompt(
            vendor_content, 
            rfp_data.get('required_scope', [])
        )
    
    elif "cost" in criteria_lower or "price" in criteria_lower or "budget" in criteria_lower:
        vendor_budget = vendor_data.get('rfp_responses', {}).get('budget_proposed_sar', 'Not specified')
        return get_cost_effectiveness_prompt(
            vendor_content,
            rfp_data.get('budget_sar', 0),
            vendor_budget
        )
    
    elif "timeline" in criteria_lower or "schedule" in criteria_lower or "time" in criteria_lower:
        vendor_timeline = vendor_data.get('rfp_responses', {}).get('timeline_proposed_days', 'Not specified')
        return get_timeline_feasibility_prompt(
            vendor_content,
            rfp_data.get('timeline_days', 0),
            vendor_timeline
        )
    
    elif "experience" in criteria_lower or "track" in criteria_lower or "history" in criteria_lower:
        return get_company_experience_prompt(
            vendor_content,
            rfp_data.get('project_name', 'Unknown Project')
        )
    
    elif "support" in criteria_lower or "maintenance" in criteria_lower or "service" in criteria_lower:
        return get_support_prompt(
            vendor_content,
            rfp_data.get('mandatory_requirements', [])
        )
    
    else:
        # Generic criteria evaluation
        return get_generic_criteria_prompt(criteria_name, vendor_content, rfp_data)

def get_generic_criteria_prompt(criteria_name: str, vendor_content: str, rfp_data: Dict[str, Any]) -> str:
    """Generic prompt for custom/unknown evaluation criteria"""
    
    return f"""
You are evaluating a vendor on the criteria: {criteria_name.upper()}

{get_scoring_scale_definition()}

PROJECT CONTEXT:
- Project: {rfp_data.get('project_name', 'Unknown')}
- Scope: {', '.join(rfp_data.get('required_scope', [])[:3])}...

VENDOR PROPOSAL CONTENT:
{vendor_content}

Evaluate the vendor on "{criteria_name}" based on:
1. How well the vendor addresses this specific criteria
2. Evidence provided in the proposal
3. Relevance and quality of vendor's approach
4. Completeness of response to this evaluation dimension

Provide objective assessment based on proposal content.

Return ONLY a JSON object:
{{
    "score": <1-10 integer>,
    "justification": "Detailed evaluation for {criteria_name}",
    "strengths": ["Advantages for this criteria"],
    "weaknesses": ["Gaps or concerns for this criteria"],
    "confidence": "high|medium|low"
}}
""" 