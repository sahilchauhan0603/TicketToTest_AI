"""
Quick Test Script
Run this to verify everything is working before demo
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from agents import AgentOrchestrator, TicketInfo
        from utils import ExcelExporter, get_sample_ticket
        import streamlit
        import openpyxl
        import google.generativeai as genai
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_sample_tickets():
    """Test that sample tickets load"""
    print("\nTesting sample tickets...")
    try:
        from utils.sample_tickets import get_sample_ticket, SAMPLE_TICKETS
        
        for ticket_type in ['bug_fix', 'feature', 'api_change']:
            ticket = get_sample_ticket(ticket_type)
            assert ticket['ticket_id'], f"Missing ticket_id for {ticket_type}"
            assert ticket['title'], f"Missing title for {ticket_type}"
            print(f"✓ {ticket_type}: {ticket['ticket_id']}")
        
        print("✓ All sample tickets loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Sample tickets failed: {e}")
        return False


def test_api_key():
    """Test API key configuration"""
    print("\nTesting API key...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("✗ GOOGLE_API_KEY not found in .env file")
        print("  Please copy .env.example to .env and add your API key")
        return False
    
    if api_key.startswith('your_'):
        print("✗ GOOGLE_API_KEY appears to be a placeholder value")
        return False
    
    # Test API connection
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
        model = genai.GenerativeModel(model_name=model_name)
        # Simple test call
        response = model.generate_content("test")
        print(f"✓ API key valid and working (using {model_name})")
        return True
    except Exception as e:
        print(f"✗ API test failed: {e}")
        print("  Check your API key and Google AI account")
        return False


def test_orchestrator():
    """Test that orchestrator can be initialized"""
    print("\nTesting agent orchestrator...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⊘ Skipping (no API key)")
        return True
    
    try:
        from agents import AgentOrchestrator
        orchestrator = AgentOrchestrator(api_key)
        print("✓ Orchestrator initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Orchestrator failed: {e}")
        return False


def test_excel_export():
    """Test Excel export functionality"""
    print("\nTesting Excel export...")
    try:
        from utils import ExcelExporter, get_sample_ticket
        from agents.state import create_initial_state, TestCase
        
        # Create a dummy state
        ticket = get_sample_ticket('bug_fix')
        state = create_initial_state(ticket)
        
        # Add a dummy test case
        state['test_cases'].append(TestCase(
            test_id="TEST-001",
            title="Sample Test Case",
            priority="P1",
            category="Happy Path",
            preconditions="User is logged in",
            test_steps=["Step 1", "Step 2", "Step 3"],
            expected_result="Success",
            test_data="test@example.com",
            automation_feasibility="High"
        ))
        
        # Test export
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_export.xlsx"
        
        exporter = ExcelExporter()
        exporter.export_test_cases(state, str(output_path))
        
        if output_path.exists():
            print(f"✓ Excel export successful: {output_path}")
            output_path.unlink()  # Clean up
            return True
        else:
            print("✗ Excel file not created")
            return False
            
    except Exception as e:
        print(f"✗ Excel export failed: {e}")
        return False


def test_full_pipeline():
    """Test full pipeline with sample ticket (requires API key)"""
    print("\nTesting full pipeline...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⊘ Skipping (no API key)")
        return True
    
    try:
        from agents import AgentOrchestrator
        from utils import get_sample_ticket
        
        print("  Initializing orchestrator...")
        orchestrator = AgentOrchestrator(api_key)
        
        print("  Loading sample ticket...")
        ticket = get_sample_ticket('bug_fix')
        
        print("  Processing ticket (this will take ~15-20 seconds)...")
        final_state = orchestrator.process_ticket(ticket)
        
        test_cases = len(final_state.get('test_cases', []))
        processing_time = final_state.get('processing_time', 0)
        
        print(f"✓ Pipeline successful!")
        print(f"  - Generated {test_cases} test cases")
        print(f"  - Processing time: {processing_time:.2f}s")
        
        return test_cases > 0
        
    except Exception as e:
        print(f"✗ Full pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Ticket-to-Test AI - System Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Sample Tickets", test_sample_tickets),
        ("API Key", test_api_key),
        ("Orchestrator", test_orchestrator),
        ("Excel Export", test_excel_export),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results.append((name, False))
    
    # Ask about full pipeline test
    print("\n" + "=" * 60)
    print("Optional: Full Pipeline Test (uses API credits)")
    response = input("Run full pipeline test? (y/N): ").strip().lower()
    
    if response == 'y':
        result = test_full_pipeline()
        results.append(("Full Pipeline", result))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready for the demo!")
        print("\nNext steps:")
        print("  1. Run: python -m streamlit run app.py")
        print("  2. Open http://localhost:8501")
        print("  3. Select a sample ticket")
        print("  4. Click 'Generate Test Cases'")
    else:
        print("\n⚠ Some tests failed. Please fix before demo.")
        print("Check INSTALLATION.md for troubleshooting steps.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
