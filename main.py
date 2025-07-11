import json
import os

from superlinked import framework as sl
import pandas as pd

from typing import List
from datetime import datetime
import sample_data
import pdf_processor

# Configuration: Switch between modes
TEST_MODE = "pdf"  # Options: "sample" or "pdf"

class VendorProposal(sl.Schema):
    id: sl.IdField
    vendor_name: sl.String
    project_name: sl.String
    time_stamp: sl.String
    price: sl.Float
    delivery_timeline: sl.String
    scope_summary: sl.String
    risks: sl.String


vendor_proposal = VendorProposal()

scope_space = sl.TextSimilaritySpace(
    text=vendor_proposal.scope_summary,
    model="sentence-transformers/all-MiniLM-L6-v2"
)

price_space = sl.NumberSpace(
    number=vendor_proposal.price, min_value=0, max_value=1000000, mode=sl.Mode.MAXIMUM
)

risks_space = sl.TextSimilaritySpace(
    text=vendor_proposal.risks,
    model="sentence-transformers/all-MiniLM-L6-v2"
)

# Create index combining all spaces
# Note: Spaces = what we can search BY, Fields = what we get back in results
# Without fields, we'd only get vectorized data, not complete proposal info
procurement_index = sl.Index(
    [scope_space, price_space, risks_space],
    fields=[
        vendor_proposal.id,
        vendor_proposal.vendor_name,
        vendor_proposal.project_name,
        vendor_proposal.time_stamp,
        vendor_proposal.price,
        vendor_proposal.delivery_timeline,
        vendor_proposal.scope_summary,
        vendor_proposal.risks
    ]
)

# Create query with weighted search across all spaces
procurement_query = (
    sl.Query(
        procurement_index,
        weights={
            scope_space: sl.Param("scope_weight"),
            price_space: sl.Param("price_weight"),
            risks_space: sl.Param("risks_weight"),
        },
    )
    .find(vendor_proposal)
    .similar(
        scope_space,
        sl.Param(
            "scope_query",
            description="Text describing the project scope or type of work.",
        ),
    )
    .similar(
        risks_space,
        sl.Param(
            "risks_query", 
            description="Text describing risks or concerns to search for.",
        ),
    )
    .select_all()
    .limit(sl.Param("limit"))
)


# Create source for data storage
source = sl.InMemorySource(vendor_proposal)

# Create executor connecting source and index
executor = sl.InMemoryExecutor(sources=[source], indices=[procurement_index])

# Create and run the app
app = executor.run()


if __name__ == "__main__":
    print("Hello, World!")
    print("✅ Schema created successfully!")
    print("✅ Vector spaces created successfully!")
    print("✅ Index created successfully!")
    print("✅ Query created successfully!")
    print("✅ Source created successfully!")
    print("✅ Executor created successfully!")
    print("✅ App created successfully!")
    print("🚀 System is LIVE and ready for data!")
    
    print(f"\n🔧 Running in {TEST_MODE.upper()} mode...")
    
    if TEST_MODE == "sample":
        # Sample data testing mode
        print("\n📝 Adding sample vendor proposals...")
        sample_proposals = sample_data.get_sample_proposals()
        source.put(sample_proposals)
        print("✅ Sample data added successfully!")
        
        # Run comprehensive search tests
        sample_data.run_search_tests(app, procurement_query, sl)
        
    elif TEST_MODE == "pdf":
        # PDF processing mode
        print("\n📄 PDF processing mode - Processing real proposal files!")
        
        # Process PDF proposals
        pdf_proposals = pdf_processor.process_pdf_proposals()
        
        if pdf_proposals:
            # Add extracted data to Superlinked
            source.put(pdf_proposals)
            print("✅ PDF data indexed successfully!")
            
            # Run PDF-specific search tests
            pdf_processor.run_pdf_tests(app, procurement_query, sl, pdf_proposals)
        else:
            print("❌ No PDF proposals were processed")
            print("💡 Make sure you have PDF files in data/proposals/ directory")
        
    else:
        print("❌ Invalid TEST_MODE. Please set to 'sample' or 'pdf'")
        
    print("\n🎉 All operations completed successfully!")
    print("🚀 Your AI Procurement Agent is working perfectly!")

    