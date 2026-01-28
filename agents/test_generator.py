"""
Test Case Generator Agent
Generates detailed, structured test cases from the QA roadmap
"""
from typing import Dict, List
import json
import google.generativeai as genai
from agents.state import AgentState, TestCase, log_agent_action
import os


class TestGeneratorAgent:
    """
    Agent that generates detailed test cases with steps, expected results, and metadata
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "TestGeneratorAgent"
    
    def process(self, state: AgentState) -> AgentState:
        """
        Generate detailed test cases from QA roadmap
        """
        state["current_agent"] = self.name
        
        # Generate test cases for each category
        for category, scenarios in state["qa_roadmap"].items():
            test_cases = self._generate_test_cases_for_category(state, category, scenarios)
            state["test_cases"].extend(test_cases)
        
        # Log action
        log_agent_action(state, self.name, "generated_test_cases", {
            "total_test_cases": len(state["test_cases"]),
            "by_priority": self._count_by_priority(state["test_cases"])
        })
        
        return state
    
    def _generate_test_cases_for_category(
        self, 
        state: AgentState, 
        category: str, 
        scenarios: List[str]
    ) -> List[TestCase]:
        """Generate test cases for a specific category"""
        
        # Build prompt
        prompt = self._build_generation_prompt(state, category, scenarios)
        
        # Call Gemini
        model = self.llm.GenerativeModel(
            model_name=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
        )
        full_prompt = f"{self._get_system_prompt()}\n\n{prompt}"
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        
        # Convert to TestCase format
        test_cases = []
        for idx, tc in enumerate(result.get("test_cases", [])):
            test_case = TestCase(
                test_id=f"{state['ticket_info']['ticket_id']}_TC{len(state['test_cases']) + idx + 1:03d}",
                title=tc.get("title", ""),
                priority=tc.get("priority", "P2"),
                category=category,
                preconditions=tc.get("preconditions", ""),
                test_steps=tc.get("test_steps", []),
                expected_result=tc.get("expected_result", ""),
                test_data=tc.get("test_data"),
                automation_feasibility=tc.get("automation_feasibility", "Medium")
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _get_system_prompt(self) -> str:
        return """You are an expert QA engineer who writes detailed, executable test cases.

For each scenario, create a structured test case with:
- Clear, descriptive title
- Priority (P0: Critical, P1: High, P2: Medium, P3: Low)
- Preconditions (system state, test data setup)
- Detailed test steps (numbered, actionable)
- Expected result (specific, measurable)
- Test data (if applicable)
- Automation feasibility (High/Medium/Low)

Return JSON:
{
    "test_cases": [
        {
            "title": "Test case title",
            "priority": "P0/P1/P2/P3",
            "preconditions": "What needs to be set up",
            "test_steps": ["Step 1", "Step 2", ...],
            "expected_result": "What should happen",
            "test_data": "Specific data needed (optional)",
            "automation_feasibility": "High/Medium/Low"
        },
        ...
    ]
}

Make test cases specific, actionable, and complete."""
    
    def _build_generation_prompt(
        self, 
        state: AgentState, 
        category: str, 
        scenarios: List[str]
    ) -> str:
        """Build generation prompt for test cases"""
        
        ticket = state["ticket_info"]
        requirements = state["extracted_requirements"]
        
        return f"""Generate detailed test cases for the {category} category.

**Ticket:** {ticket.get('ticket_id')} - {ticket.get('title')}
**Priority:** {ticket.get('priority')}

**Requirements:**
{chr(10).join(f"- {req}" for req in requirements[:10])}  # Limit for token efficiency

**Test Scenarios for {category}:**
{chr(10).join(f"- {scenario}" for scenario in scenarios)}

Generate complete, executable test cases for each scenario."""
    
    def _count_by_priority(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """Count test cases by priority"""
        counts = {}
        for tc in test_cases:
            priority = tc.get("priority", "P2")
            counts[priority] = counts.get(priority, 0) + 1
        return counts
