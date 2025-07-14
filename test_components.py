#!/usr/bin/env python3
"""
Test script for AI Procurement Agent components
Usage: python test_components.py [component]
"""

import sys
import argparse
import pdf_processor
from superlinked import framework as sl
from main import app, procurement_query

def test_pdf_processing():
    """Test PDF processing pipeline"""
    print("Testing PDF Processing...")
    proposals = pdf_processor.process_pdf_proposals()
    
    if proposals:
        print(f"Successfully processed {len(proposals)} proposals")
        for p in proposals:
            print(f"   • {p['vendor_name']}: ${p['price']:,.0f} - {p['project_name']}")
        return proposals
    else:
        print("No proposals found")
        return []

def test_comparison_report(proposals=None):
    """Test comparison report generation"""
    print("\nTesting Comparison Report...")
    
    if not proposals:
        proposals = pdf_processor.process_pdf_proposals()
    
    if proposals:
        report = pdf_processor.generate_comparison_report(proposals)
        print("Comparison report generated successfully!")
        return report
    else:
        print("No proposals to compare")
        return None

def test_recommendations(proposals=None):
    """Test recommendation system"""
    print("\nTesting Recommendation System...")
    
    if not proposals:
        proposals = pdf_processor.process_pdf_proposals()
    
    if proposals:
        # Test balanced recommendations
        recommendations = pdf_processor.recommend_best_proposals(
            app, procurement_query, sl, proposals, 
            evaluation_profile="balanced", limit=3
        )
        
        if recommendations and not recommendations.get("error"):
            print("Recommendations generated successfully!")
            for i, rec in enumerate(recommendations["recommendations"][:3], 1):
                print(f"   {i}. {rec['vendor_name']}: ${rec['price']:,.0f} (Score: {rec.get('final_score', 'N/A')})")
            return recommendations
        else:
            print(f"Recommendation failed: {recommendations.get('error', 'Unknown error')}")
    else:
        print("No proposals for recommendations")
        return None

def test_executive_summary(proposals=None, comparison=None, recommendations=None):
    """Test executive summary generation"""
    print("\nTesting Executive Summary...")
    
    if not proposals:
        proposals = pdf_processor.process_pdf_proposals()
    
    if proposals:
        exec_report = pdf_processor.generate_executive_summary_report(
            proposals, comparison, recommendations
        )
        
        if exec_report and not exec_report.get("error"):
            print("Executive summary generated successfully!")
            summary = exec_report["executive_summary"]
            print(f"   • {summary['overview']}")
            print(f"   • {summary['key_finding']}")
            print(f"   • Critical issues: {summary['critical_issues']}")
            return exec_report
        else:
            print(f"Executive summary failed: {exec_report.get('error', 'Unknown error')}")
    else:
        print("No proposals for executive summary")
        return None

def test_search_functionality(proposals=None):
    """Test search functionality"""
    print("\nTesting Search Functionality...")
    
    if not proposals:
        proposals = pdf_processor.process_pdf_proposals()
    
    if proposals:
        # Add proposals to Superlinked for testing
        from main import source
        source.put(proposals)
        
        # Test search
        result = app.query(
            procurement_query,
            scope_query="portal management",
            scope_weight=1.0,
            price_weight=0.0,
            risks_weight=0.0,
            limit=3
        )
        
        df = sl.PandasConverter.to_pandas(result)
        print(f"Search returned {len(df)} results")
        for _, row in df.iterrows():
            print(f"   • {row['vendor_name']}: {row['project_name']}")
    else:
        print("No proposals for search testing")

def test_all_components():
    """Run all component tests"""
    print("Running All Component Tests...\n")
    
    # Test in order of dependency
    proposals = test_pdf_processing()
    comparison = test_comparison_report(proposals)
    recommendations = test_recommendations(proposals)
    executive = test_executive_summary(proposals, comparison, recommendations)
    test_search_functionality(proposals)
    
    print("\nAll component tests completed!")

def main():
    parser = argparse.ArgumentParser(description='Test AI Procurement Agent components')
    parser.add_argument('component', nargs='?', default='all',
                       choices=['pdf', 'comparison', 'recommendations', 'executive', 'search', 'all'],
                       help='Component to test (default: all)')
    
    args = parser.parse_args()
    
    if args.component == 'pdf':
        test_pdf_processing()
    elif args.component == 'comparison':
        test_comparison_report()
    elif args.component == 'recommendations':
        test_recommendations()
    elif args.component == 'executive':
        test_executive_summary()
    elif args.component == 'search':
        test_search_functionality()
    elif args.component == 'all':
        test_all_components()

if __name__ == "__main__":
    main() 