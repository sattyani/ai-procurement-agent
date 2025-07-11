"""
Sample vendor proposal data for testing the AI Procurement Agent
"""

def get_sample_proposals():
    """Return sample vendor proposals for testing purposes."""
    return [
        {
            "id": 1,
            "vendor_name": "Acme Corp",
            "project_name": "E-commerce Website Development",
            "time_stamp": "2024-01-15T10:00:00Z",
            "price": 75000.0,
            "delivery_timeline": "6 months with monthly milestones, final delivery by July 2024",
            "scope_summary": "Full-stack e-commerce platform with React frontend, Node.js backend, payment processing, inventory management, and admin dashboard",
            "risks": "Third-party payment gateway integration delays, potential scope creep with additional features, dependency on client's existing inventory system"
        },
        {
            "id": 2,
            "vendor_name": "TechSolutions Inc",
            "project_name": "Mobile App Development",
            "time_stamp": "2024-01-16T14:30:00Z",
            "price": 45000.0,
            "delivery_timeline": "4 months development cycle, iOS and Android versions delivered simultaneously",
            "scope_summary": "Native mobile application for iOS and Android, user authentication, real-time notifications, offline capability, and cloud synchronization",
            "risks": "App store approval delays, device compatibility issues across different OS versions, performance optimization challenges for older devices"
        },
        {
            "id": 3,
            "vendor_name": "DataWise Solutions",
            "project_name": "Business Intelligence Dashboard",
            "time_stamp": "2024-01-17T09:15:00Z",
            "price": 120000.0,
            "delivery_timeline": "8 months implementation with training, phased rollout starting month 6",
            "scope_summary": "Enterprise business intelligence platform with data visualization, automated reporting, predictive analytics, and integration with existing ERP systems",
            "risks": "Data migration complexity, user adoption challenges, integration timeline dependent on ERP system availability, potential performance issues with large datasets"
        },
        {
            "id": 4,
            "vendor_name": "CloudFirst Technologies",
            "project_name": "Cloud Migration Services",
            "time_stamp": "2024-01-18T11:45:00Z",
            "price": 95000.0,
            "delivery_timeline": "5 months migration with 2 weeks testing buffer, go-live in month 6",
            "scope_summary": "Complete cloud infrastructure migration from on-premises to AWS, including database migration, application modernization, and security setup",
            "risks": "Data migration downtime, application compatibility issues, security configuration challenges, potential cost overruns due to unexpected AWS usage"
        },
        {
            "id": 5,
            "vendor_name": "AI Innovations Lab",
            "project_name": "Machine Learning Platform",
            "time_stamp": "2024-01-19T16:20:00Z",
            "price": 150000.0,
            "delivery_timeline": "10 months development with POC in month 3, beta in month 7, production in month 10",
            "scope_summary": "Custom machine learning platform for predictive analytics, automated model training, real-time inference API, and comprehensive monitoring dashboard",
            "risks": "Model accuracy requirements may not be met, data quality issues, integration complexity with existing systems, longer than expected training time for complex models"
        }
    ]


def run_search_tests(app, procurement_query, sl):
    """Run comprehensive search tests on the sample data."""
    print("\n🔍 Testing search functionality...")
    
    # Test 1: Search for web development projects
    print("\n1. Searching for 'web development' projects:")
    result1 = app.query(
        procurement_query,
        scope_query="web development website",
        scope_weight=1.0,
        price_weight=0.0,
        risks_weight=0.0,
        limit=2
    )
    df1 = sl.PandasConverter.to_pandas(result1)
    print(f"Found {len(df1)} results:")
    for _, row in df1.iterrows():
        print(f"   • {row['vendor_name']}: {row['project_name']} (${row['price']:,.0f})")
    
    # Test 2: Search for mobile projects
    print("\n2. Searching for 'mobile app' projects:")
    result2 = app.query(
        procurement_query,
        scope_query="mobile app development",
        scope_weight=1.0,
        price_weight=0.0,
        risks_weight=0.0,
        limit=2
    )
    df2 = sl.PandasConverter.to_pandas(result2)
    print(f"Found {len(df2)} results:")
    for _, row in df2.iterrows():
        print(f"   • {row['vendor_name']}: {row['project_name']} (${row['price']:,.0f})")
    
    # Test 3: Search for integration risks
    print("\n3. Searching for 'integration' risks:")
    result3 = app.query(
        procurement_query,
        risks_query="integration compatibility issues",
        scope_weight=0.0,
        price_weight=0.0,
        risks_weight=1.0,
        limit=3
    )
    df3 = sl.PandasConverter.to_pandas(result3)
    print(f"Found {len(df3)} results:")
    for _, row in df3.iterrows():
        print(f"   • {row['vendor_name']}: {row['risks'][:100]}...")
    
    # Test 4: Search for cloud projects
    print("\n4. Searching for 'cloud infrastructure' projects:")
    result4 = app.query(
        procurement_query,
        scope_query="cloud infrastructure migration",
        scope_weight=1.0,
        price_weight=0.0,
        risks_weight=0.0,
        limit=2
    )
    df4 = sl.PandasConverter.to_pandas(result4)
    print(f"Found {len(df4)} results:")
    for _, row in df4.iterrows():
        print(f"   • {row['vendor_name']}: {row['project_name']} (${row['price']:,.0f})")
    
    # Test 5: Search for AI/ML projects
    print("\n5. Searching for 'machine learning' projects:")
    result5 = app.query(
        procurement_query,
        scope_query="machine learning artificial intelligence",
        scope_weight=1.0,
        price_weight=0.0,
        risks_weight=0.0,
        limit=2
    )
    df5 = sl.PandasConverter.to_pandas(result5)
    print(f"Found {len(df5)} results:")
    for _, row in df5.iterrows():
        print(f"   • {row['vendor_name']}: {row['project_name']} (${row['price']:,.0f})")
    
    print("\n🎉 All search tests completed successfully!") 