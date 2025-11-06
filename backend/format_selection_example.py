#!/usr/bin/env python3
"""
Example showing how data format is selected based on NLP analysis needs.
"""

def demonstrate_format_selection():
    """Show how format selection works."""
    
    scenarios = [
        {
            "query": "Find product gaps for Netflix based on user reviews",
            "needs_nlp_analysis": True,
            "expected_format": "csv",
            "reason": "NLP analysis needs text data in CSV format for better processing"
        },
        {
            "query": "Show me the exact review data for Netflix with ratings below 3",
            "needs_nlp_analysis": False,
            "expected_format": "json",
            "reason": "Direct data query uses JSON for structured data handling"
        },
        {
            "query": "Analyze sentiment patterns in Spotify user feedback",
            "needs_nlp_analysis": True,
            "expected_format": "csv",
            "reason": "Sentiment analysis requires CSV format for text processing"
        },
        {
            "query": "Get the count of reviews by rating for each company",
            "needs_nlp_analysis": False,
            "expected_format": "json",
            "reason": "Aggregated data query uses JSON for structured results"
        }
    ]
    
    print("Data Format Selection Examples")
    print("=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Query: {scenario['query']}")
        print(f"   NLP Analysis Needed: {scenario['needs_nlp_analysis']}")
        print(f"   Selected Format: {scenario['expected_format']}")
        print(f"   Reason: {scenario['reason']}")
    
    print("\n" + "=" * 50)
    print("Format Selection Logic:")
    print("• CSV format → Better for NLP text processing")
    print("• JSON format → Better for structured data queries")

if __name__ == "__main__":
    demonstrate_format_selection()