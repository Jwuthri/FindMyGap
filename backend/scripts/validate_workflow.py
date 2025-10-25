"""
Comprehensive validation script for Product Gap Workflow implementation.
This script verifies all components are properly implemented.
"""

import sys
from typing import List, Tuple

def test_imports() -> Tuple[bool, str]:
    """Test all necessary imports."""
    try:
        from app.agents import create_product_gap_workflow
        from app.agents.product_gap_workflow import (
            QueryAnalysis,
            DataSufficiencyResult,
            create_query_analyzer_agent,
            create_database_retrieval_agent,
            create_data_sufficiency_agent,
            create_nlp_analysis_agent,
            create_output_format_agent,
            create_answer_writer_team,
        )
        return True, "✓ All imports successful"
    except Exception as e:
        return False, f"✗ Import failed: {e}"


def test_schema_models() -> Tuple[bool, str]:
    """Test Pydantic schemas are properly defined."""
    try:
        from app.agents.product_gap_workflow import QueryAnalysis, DataSufficiencyResult
        
        # Test QueryAnalysis
        qa = QueryAnalysis(
            needs_data_retrieval=True,
            needs_nlp_analysis=True,
            company="spotify",
            query_type="gap_analysis",
            reasoning="Test reasoning"
        )
        
        # Test DataSufficiencyResult
        dsr = DataSufficiencyResult(
            is_sufficient=False,
            current_count=50,
            recommended_count=150,
            reasoning="Need more data"
        )
        
        return True, "✓ Schema models work correctly"
    except Exception as e:
        return False, f"✗ Schema validation failed: {e}"


def test_agent_creation() -> Tuple[bool, str]:
    """Test all agents can be created."""
    try:
        from app.agents.product_gap_workflow import (
            create_query_analyzer_agent,
            create_database_retrieval_agent,
            create_data_sufficiency_agent,
            create_nlp_analysis_agent,
            create_output_format_agent,
            create_answer_writer_team,
        )
        from agno.models.openai import OpenAIChat
        from app.config import SETTINGS
        
        model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
        
        agents = [
            create_query_analyzer_agent(model),
            create_database_retrieval_agent(model),
            create_data_sufficiency_agent(model),
            create_nlp_analysis_agent(model),
            create_output_format_agent(model),
            create_answer_writer_team(model),
        ]
        
        return True, f"✓ All {len(agents)} agents created successfully"
    except Exception as e:
        return False, f"✗ Agent creation failed: {e}"


def test_workflow_creation() -> Tuple[bool, str]:
    """Test workflow can be created."""
    try:
        from app.agents import create_product_gap_workflow
        from app.config import SETTINGS
        
        workflow = create_product_gap_workflow(
            api_key=SETTINGS.OPENAI_API_KEY,
            db_file="tmp/test_workflow.db"
        )
        
        assert workflow.name == "Product Gap Detection Workflow"
        assert len(workflow.steps) > 0
        
        return True, f"✓ Workflow created with {len(workflow.steps)} steps"
    except Exception as e:
        return False, f"✗ Workflow creation failed: {e}"


def test_tool_imports() -> Tuple[bool, str]:
    """Test all tools from teams.py are accessible."""
    try:
        from app.agents.teams import (
            retrieve_reviews,
            filter_reviews_by_rating,
            filter_reviews_by_source,
            search_reviews_by_keyword,
            list_available_companies,
            compute_tfidf,
            analyze_sentiment_distribution,
            identify_feature_requests,
            cluster_similar_reviews,
            analyze_product_gaps,
            determine_best_output_format,
        )
        
        return True, "✓ All 11 tools imported from teams.py"
    except Exception as e:
        return False, f"✗ Tool import failed: {e}"


def test_step_functions() -> Tuple[bool, str]:
    """Test all step functions exist."""
    try:
        from app.agents.product_gap_workflow import (
            query_analysis_step,
            data_retrieval_prep,
            data_sufficiency_prep,
            nlp_analysis_prep,
            format_detection_prep,
            answer_writing_prep,
        )
        
        return True, "✓ All 6 step functions defined"
    except Exception as e:
        return False, f"✗ Step function check failed: {e}"


def run_all_tests():
    """Run all validation tests."""
    print("=" * 80)
    print("PRODUCT GAP WORKFLOW - VALIDATION SUITE")
    print("=" * 80)
    print()
    
    tests = [
        ("Import Tests", test_imports),
        ("Schema Models", test_schema_models),
        ("Agent Creation", test_agent_creation),
        ("Workflow Creation", test_workflow_creation),
        ("Tool Imports", test_tool_imports),
        ("Step Functions", test_step_functions),
    ]
    
    results: List[Tuple[str, bool, str]] = []
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}...", end=" ")
        success, message = test_func()
        results.append((test_name, success, message))
        print(message)
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, message in results:
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}: {message}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All validation tests passed!")
        print("✓ Product Gap Workflow is ready for use")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        print("✗ Please review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

