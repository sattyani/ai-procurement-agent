"""
Vendor Evaluation Engine
Scores vendors on evaluation criteria and calculates weighted rankings
"""

import json
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from evaluation_prompts import get_evaluation_prompt_for_criteria
from rfp_schema import load_rfp

class VendorEvaluationEngine:
    """AI-powered vendor evaluation and scoring system"""
    
    def __init__(self, rfp_json_path: str):
        """
        Initialize evaluation engine
        
        Args:
            rfp_json_path: Path to extracted RFP JSON file
        """
        self.rfp_json_path = rfp_json_path
        self.rfp_data = None
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=2000)
        
    def load_rfp_data(self) -> bool:
        """Load RFP data for evaluation context"""
        self.rfp_data = load_rfp(self.rfp_json_path)
        if not self.rfp_data:
            print(f"Error: Could not load RFP data from {self.rfp_json_path}")
            return False
        return True
    
    def load_vendor_proposal_content(self, pdf_path: str) -> str:
        """Load full text content from vendor proposal PDF"""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            content = "\n\n".join([doc.page_content for doc in documents])
            return content
        except Exception as e:
            print(f"Error loading vendor PDF {pdf_path}: {e}")
            return ""
    
    def score_vendor_on_criteria(self, criteria_name: str, vendor_content: str, 
                                vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a vendor on a specific evaluation criteria
        
        Args:
            criteria_name: Name of evaluation criteria
            vendor_content: Full vendor proposal text
            vendor_data: Extracted vendor data from previous analysis
            
        Returns:
            Dictionary with score, justification, strengths, weaknesses, confidence
        """
        
        if not self.rfp_data:
            raise ValueError("RFP data not loaded. Call load_rfp_data() first.")
        
        # Get appropriate prompt for this criteria
        prompt = get_evaluation_prompt_for_criteria(
            criteria_name, vendor_content, self.rfp_data, vendor_data
        )
        
        try:
            # Send to AI for evaluation
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            # Clean and parse response
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            evaluation_result = json.loads(response_text)
            
            # Validate score is in range
            score = evaluation_result.get('score', 0)
            if not isinstance(score, int) or score < 1 or score > 10:
                print(f"Warning: Invalid score {score} for {criteria_name}, defaulting to 5")
                evaluation_result['score'] = 5
                evaluation_result['confidence'] = 'low'
            
            return evaluation_result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {criteria_name}: {e}")
            return {
                'score': 5,
                'justification': f'Error parsing AI response for {criteria_name}',
                'strengths': [],
                'weaknesses': ['Could not evaluate due to parsing error'],
                'confidence': 'low'
            }
        except Exception as e:
            print(f"Evaluation error for {criteria_name}: {e}")
            return {
                'score': 5,
                'justification': f'Error evaluating {criteria_name}: {str(e)}',
                'strengths': [],
                'weaknesses': ['Could not evaluate due to system error'],
                'confidence': 'low'
            }
    
    def evaluate_vendor_full(self, pdf_path: str, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete evaluation of a vendor across all RFP criteria
        
        Args:
            pdf_path: Path to vendor proposal PDF
            vendor_data: Previously extracted vendor data
            
        Returns:
            Complete evaluation results with scores, weights, and ranking
        """
        
        vendor_name = vendor_data.get('vendor_name', 'Unknown')
        print(f"\nEvaluating: {vendor_name}")
        print("-" * 50)
        
        # Load vendor proposal content
        vendor_content = self.load_vendor_proposal_content(pdf_path)
        if not vendor_content:
            print(f"  Error: Could not load proposal content")
            return None
        
        # Get evaluation criteria from RFP
        evaluation_criteria = self.rfp_data.get('evaluation_criteria', {})
        if not evaluation_criteria:
            print(f"  Error: No evaluation criteria found in RFP")
            return None
        
        print(f"  Scoring on {len(evaluation_criteria)} criteria...")
        
        # Score vendor on each criteria
        scores = {}
        total_weighted_score = 0.0
        
        for criteria_name, weight in evaluation_criteria.items():
            print(f"    Evaluating: {criteria_name}...")
            
            evaluation = self.score_vendor_on_criteria(
                criteria_name, vendor_content, vendor_data
            )
            
            # Calculate weighted score
            raw_score = evaluation['score']
            weighted_score = raw_score * weight
            total_weighted_score += weighted_score
            
            scores[criteria_name] = {
                'raw_score': raw_score,
                'weight': weight,
                'weighted_score': weighted_score,
                'justification': evaluation['justification'],
                'strengths': evaluation['strengths'],
                'weaknesses': evaluation['weaknesses'],
                'confidence': evaluation['confidence']
            }
            
            print(f"      Score: {raw_score}/10 (Weight: {weight:.1%}) = {weighted_score:.2f}")
        
        # Calculate overall confidence
        confidences = [scores[c]['confidence'] for c in scores]
        high_conf = confidences.count('high')
        medium_conf = confidences.count('medium')
        
        if high_conf >= len(confidences) * 0.7:
            overall_confidence = 'high'
        elif high_conf + medium_conf >= len(confidences) * 0.5:
            overall_confidence = 'medium'
        else:
            overall_confidence = 'low'
        
        print(f"  Total Weighted Score: {total_weighted_score:.2f}/10")
        print(f"  Overall Confidence: {overall_confidence}")
        
        return {
            'vendor_name': vendor_name,
            'pdf_path': pdf_path,
            'total_weighted_score': round(total_weighted_score, 2),
            'overall_confidence': overall_confidence,
            'criteria_scores': scores,
            'evaluation_summary': {
                'strengths': self._aggregate_strengths(scores),
                'weaknesses': self._aggregate_weaknesses(scores),
                'recommendation': self._generate_recommendation(total_weighted_score, overall_confidence)
            }
        }
    
    def _aggregate_strengths(self, scores: Dict[str, Any]) -> List[str]:
        """Aggregate strengths across all criteria"""
        all_strengths = []
        for criteria, data in scores.items():
            for strength in data['strengths']:
                all_strengths.append(f"{criteria}: {strength}")
        return all_strengths[:5]  # Top 5 strengths
    
    def _aggregate_weaknesses(self, scores: Dict[str, Any]) -> List[str]:
        """Aggregate weaknesses across all criteria"""
        all_weaknesses = []
        for criteria, data in scores.items():
            for weakness in data['weaknesses']:
                all_weaknesses.append(f"{criteria}: {weakness}")
        return all_weaknesses[:5]  # Top 5 weaknesses
    
    def _generate_recommendation(self, total_score: float, confidence: str) -> str:
        """Generate overall recommendation based on score and confidence"""
        if total_score >= 8.0 and confidence == 'high':
            return "STRONGLY RECOMMENDED - Excellent vendor with high confidence evaluation"
        elif total_score >= 7.0 and confidence in ['high', 'medium']:
            return "RECOMMENDED - Good vendor with reliable evaluation"
        elif total_score >= 6.0:
            return "CONDITIONALLY RECOMMENDED - Average vendor, consider alternatives"
        elif total_score >= 5.0:
            return "NOT RECOMMENDED - Below average performance"
        else:
            return "STRONGLY NOT RECOMMENDED - Poor vendor performance"
    
    def rank_vendors(self, vendor_evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank vendors by weighted score
        
        Args:
            vendor_evaluations: List of vendor evaluation results
            
        Returns:
            Sorted list of vendors (highest score first)
        """
        
        # Sort by total weighted score (descending)
        ranked_vendors = sorted(
            vendor_evaluations,
            key=lambda v: v['total_weighted_score'],
            reverse=True
        )
        
        # Add rank numbers
        for i, vendor in enumerate(ranked_vendors, 1):
            vendor['rank'] = i
        
        return ranked_vendors
    
    def generate_evaluation_matrix(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate evaluation matrix for all vendors"""
        
        if not vendor_evaluations:
            return "No vendor evaluations to display"
        
        # Get criteria names from first vendor
        criteria_names = list(vendor_evaluations[0]['criteria_scores'].keys())
        
        # Create header
        matrix = "\nVENDOR EVALUATION MATRIX\n"
        matrix += "=" * 100 + "\n"
        
        # Column headers
        header = f"{'Vendor':<25}"
        for criteria in criteria_names:
            header += f" | {criteria[:12]:<12}"
        header += f" | {'Total':<6} | {'Rank':<4}"
        matrix += header + "\n"
        matrix += "-" * 100 + "\n"
        
        # Vendor rows
        for vendor in vendor_evaluations:
            row = f"{vendor['vendor_name'][:24]:<25}"
            
            for criteria in criteria_names:
                score = vendor['criteria_scores'][criteria]['raw_score']
                row += f" | {score:>12}"
            
            total = vendor['total_weighted_score']
            rank = vendor['rank']
            row += f" | {total:>6.1f} | {rank:>4}"
            matrix += row + "\n"
        
        return matrix

def evaluate_all_vendors(rfp_json_path: str = "outputs/rfp_analysis/smart_parking_extracted.json",
                        vendor_analyses: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Main function to evaluate all vendors using the evaluation engine
    
    Args:
        rfp_json_path: Path to RFP analysis JSON
        vendor_analyses: Dictionary of vendor analysis results
        
    Returns:
        List of ranked vendor evaluations
    """
    
    engine = VendorEvaluationEngine(rfp_json_path)
    
    if not engine.load_rfp_data():
        return []
    
    if not vendor_analyses:
        print("No vendor analyses provided")
        return []
    
    print("ADVANCED VENDOR EVALUATION")
    print("=" * 60)
    
    evaluations = []
    
    for pdf_path, vendor_data in vendor_analyses.items():
        evaluation = engine.evaluate_vendor_full(pdf_path, vendor_data)
        if evaluation:
            evaluations.append(evaluation)
    
    # Rank vendors
    ranked_evaluations = engine.rank_vendors(evaluations)
    
    # Generate advanced reports
    print(engine.generate_evaluation_matrix(ranked_evaluations))
    print(engine.generate_advanced_comparison_report(ranked_evaluations))
    
    return ranked_evaluations

class AdvancedReportGenerator:
    """Enhanced reporting with detailed analytics and AI-generated insights"""
    
    def __init__(self, rfp_data: Dict[str, Any]):
        self.rfp_data = rfp_data
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=3000)
    
    def generate_performance_gap_analysis(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Analyze performance gaps between vendors across criteria"""
        
        if len(vendor_evaluations) < 2:
            return "Need at least 2 vendors for gap analysis"
        
        best_vendor = vendor_evaluations[0]
        criteria_names = list(best_vendor['criteria_scores'].keys())
        
        analysis = "\nPERFORMANCE GAP ANALYSIS\n"
        analysis += "=" * 60 + "\n"
        
        for criteria in criteria_names:
            scores = [v['criteria_scores'][criteria]['raw_score'] for v in vendor_evaluations]
            best_score = max(scores)
            worst_score = min(scores)
            avg_score = sum(scores) / len(scores)
            gap = best_score - worst_score
            
            analysis += f"\n{criteria}:\n"
            analysis += f"  Best Score: {best_score}/10 | Worst: {worst_score}/10 | Gap: {gap} points\n"
            analysis += f"  Average: {avg_score:.1f}/10 | Range: {worst_score}-{best_score}\n"
            
            # Find who scored best/worst
            best_vendor_name = next(v['vendor_name'] for v in vendor_evaluations 
                                  if v['criteria_scores'][criteria]['raw_score'] == best_score)
            worst_vendor_name = next(v['vendor_name'] for v in vendor_evaluations 
                                   if v['criteria_scores'][criteria]['raw_score'] == worst_score)
            
            analysis += f"  Leader: {best_vendor_name} | Laggard: {worst_vendor_name}\n"
        
        return analysis
    
    def generate_risk_confidence_matrix(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate risk assessment based on confidence levels"""
        
        matrix = "\nRISK & CONFIDENCE ASSESSMENT\n"
        matrix += "=" * 60 + "\n"
        
        for vendor in vendor_evaluations:
            name = vendor['vendor_name']
            score = vendor['total_weighted_score']
            confidence = vendor['overall_confidence']
            
            # Calculate risk level
            if confidence == 'high' and score >= 7.0:
                risk = "LOW"
            elif confidence == 'medium' and score >= 6.0:
                risk = "MEDIUM"
            elif confidence == 'low' or score < 5.0:
                risk = "HIGH"
            else:
                risk = "MEDIUM-HIGH"
            
            matrix += f"{name}:\n"
            matrix += f"  Score: {score:.1f}/10 | Confidence: {confidence.upper()} | Risk: {risk}\n"
            
            # Count low confidence criteria
            low_conf_criteria = [c for c, data in vendor['criteria_scores'].items() 
                               if data['confidence'] == 'low']
            if low_conf_criteria:
                matrix += f"  Low Confidence Areas: {', '.join(low_conf_criteria)}\n"
            matrix += "\n"
        
        return matrix
    
    def generate_criteria_strength_summary(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate summary of vendor strengths by criteria"""
        
        summary = "\nVENDOR STRENGTHS BY CRITERIA\n"
        summary += "=" * 60 + "\n"
        
        if not vendor_evaluations:
            return summary + "No vendor evaluations available\n"
        
        criteria_names = list(vendor_evaluations[0]['criteria_scores'].keys())
        
        for criteria in criteria_names:
            summary += f"\n{criteria.upper()}:\n"
            
            # Sort vendors by this criteria score
            criteria_ranking = sorted(vendor_evaluations, 
                                    key=lambda v: v['criteria_scores'][criteria]['raw_score'], 
                                    reverse=True)
            
            for i, vendor in enumerate(criteria_ranking[:3], 1):
                score = vendor['criteria_scores'][criteria]['raw_score']
                strengths = vendor['criteria_scores'][criteria]['strengths'][:2]
                summary += f"  {i}. {vendor['vendor_name']} ({score}/10)\n"
                for strength in strengths:
                    summary += f"     • {strength}\n"
        
        return summary
    
    def generate_ai_executive_insights(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate AI-powered executive insights and recommendations"""
        
        if not vendor_evaluations:
            return "No vendor data available for insights"
        
        # Prepare data summary for AI analysis
        summary_data = {
            'total_vendors': len(vendor_evaluations),
            'top_vendor': {
                'name': vendor_evaluations[0]['vendor_name'],
                'score': vendor_evaluations[0]['total_weighted_score'],
                'confidence': vendor_evaluations[0]['overall_confidence']
            },
            'score_range': {
                'highest': vendor_evaluations[0]['total_weighted_score'],
                'lowest': vendor_evaluations[-1]['total_weighted_score']
            },
            'criteria_performance': {}
        }
        
        # Add criteria performance summary
        criteria_names = list(vendor_evaluations[0]['criteria_scores'].keys())
        for criteria in criteria_names:
            scores = [v['criteria_scores'][criteria]['raw_score'] for v in vendor_evaluations]
            summary_data['criteria_performance'][criteria] = {
                'average': sum(scores) / len(scores),
                'best': max(scores),
                'worst': min(scores)
            }
        
        prompt = f"""
As a senior procurement analyst, generate executive insights and strategic recommendations based on this vendor evaluation data:

EVALUATION SUMMARY:
- Total Vendors Evaluated: {summary_data['total_vendors']}
- Top Vendor: {summary_data['top_vendor']['name']} (Score: {summary_data['top_vendor']['score']:.2f}/10)
- Score Range: {summary_data['score_range']['lowest']:.2f} - {summary_data['score_range']['highest']:.2f}
- Evaluation Confidence: {summary_data['top_vendor']['confidence']}

CRITERIA PERFORMANCE:
{json.dumps(summary_data['criteria_performance'], indent=2)}

Please provide:
1. **Strategic Recommendation** (1-2 sentences)
2. **Key Market Insights** (2-3 bullet points about vendor landscape)
3. **Risk Assessment** (1-2 sentences about procurement risks)
4. **Next Steps** (2-3 actionable recommendations)

Keep the response concise, professional, and decision-focused for C-level executives.
"""
        
        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return f"\nAI EXECUTIVE INSIGHTS\n{'=' * 60}\n{response.content}"
        except Exception as e:
            return f"\nAI EXECUTIVE INSIGHTS\n{'=' * 60}\nError generating insights: {e}"
    
    def generate_detailed_justification_report(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate comprehensive justification for vendor recommendations"""
        
        if not vendor_evaluations:
            return "No vendor evaluations available"
        
        top_vendor = vendor_evaluations[0]
        report = "\nDETAILED RECOMMENDATION JUSTIFICATION\n"
        report += "=" * 80 + "\n"
        
        report += f"RECOMMENDED VENDOR: {top_vendor['vendor_name']}\n"
        report += f"Overall Score: {top_vendor['total_weighted_score']:.2f}/10\n"
        report += f"Confidence Level: {top_vendor['overall_confidence']}\n\n"
        
        report += "CRITERIA-BY-CRITERIA JUSTIFICATION:\n"
        report += "-" * 50 + "\n"
        
        for criteria, data in top_vendor['criteria_scores'].items():
            weight = data['weight']
            score = data['raw_score']
            weighted = data['weighted_score']
            justification = data['justification']
            
            report += f"\n{criteria.upper()} (Weight: {weight:.1%}):\n"
            report += f"  Score: {score}/10 (Weighted: {weighted:.2f})\n"
            report += f"  Evaluation: {justification}\n"
            
            if data['strengths']:
                report += f"  Strengths: {', '.join(data['strengths'])}\n"
            if data['weaknesses']:
                report += f"  Concerns: {', '.join(data['weaknesses'])}\n"
        
        report += f"\nCOMPETITIVE ANALYSIS:\n"
        report += "-" * 30 + "\n"
        
        if len(vendor_evaluations) > 1:
            second_vendor = vendor_evaluations[1]
            score_gap = top_vendor['total_weighted_score'] - second_vendor['total_weighted_score']
            report += f"Score advantage over 2nd place ({second_vendor['vendor_name']}): {score_gap:.2f} points\n"
            
            if len(vendor_evaluations) >= 3:
                avg_competitor_score = sum(v['total_weighted_score'] for v in vendor_evaluations[1:]) / (len(vendor_evaluations) - 1)
                report += f"Score advantage over average competitor: {top_vendor['total_weighted_score'] - avg_competitor_score:.2f} points\n"
        
        return report

    def generate_advanced_comparison_report(self, vendor_evaluations: List[Dict[str, Any]]) -> str:
        """Generate comprehensive advanced comparison report"""
        
        if not vendor_evaluations:
            return "No vendor evaluations for comparison"
        
        report = ""
        report += self.generate_performance_gap_analysis(vendor_evaluations)
        report += self.generate_risk_confidence_matrix(vendor_evaluations)
        report += self.generate_criteria_strength_summary(vendor_evaluations)
        report += self.generate_ai_executive_insights(vendor_evaluations)
        report += self.generate_detailed_justification_report(vendor_evaluations)
        
        return report

# Add the advanced reporting method to VendorEvaluationEngine class
VendorEvaluationEngine.generate_advanced_comparison_report = lambda self, vendor_evaluations: AdvancedReportGenerator(self.rfp_data).generate_advanced_comparison_report(vendor_evaluations) 