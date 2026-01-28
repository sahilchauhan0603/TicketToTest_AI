"""
Test Strategy Agent
Creates the QA execution roadmap with test categories and scenarios
"""
from typing import Dict, List
import json
import google.generativeai as genai
from agents.state import AgentState, log_agent_action
import os


class TestStrategyAgent:
    """
    Agent that builds the QA roadmap and testing strategy
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "TestStrategyAgent"
    
    def process(self, state: AgentState) -> AgentState:
        """
        Create QA roadmap with test categories and scenarios
        """
        state["current_agent"] = self.name
        
        # Build strategy prompt
        prompt = self._build_strategy_prompt(state)
        
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
        
        # Update state
        state["qa_roadmap"] = result.get("qa_roadmap", {})
        
        # Log action
        log_agent_action(state, self.name, "created_qa_roadmap", {
            "categories": list(state["qa_roadmap"].keys()),
            "total_scenarios": sum(len(v) for v in state["qa_roadmap"].values())
        })
        
        return state
    
    def _get_system_prompt(self) -> str:
        return """You are an expert QA strategist who creates comprehensive testing roadmaps.

Your task is to create a QA execution roadmap organized by test categories:
- Happy Path (core functionality works as expected)
- Negative Testing (error handling, invalid inputs)
- Edge Cases (boundary conditions, unusual scenarios)
- Regression (ensure existing functionality not broken)
- Integration (interactions with other modules)
- Performance (if applicable)
- Security (if applicable)
- Accessibility (if UI changes)

Return a JSON object with:
{
    "qa_roadmap": {
        "Happy Path": ["scenario1", "scenario2", ...],
        "Negative Testing": ["scenario1", "scenario2", ...],
        "Edge Cases": ["scenario1", "scenario2", ...],
        "Regression": ["scenario1", "scenario2", ...],
        ...
    }
}

Be specific and actionable. Each scenario should clearly state what to test."""
    
    def _build_strategy_prompt(self, state: AgentState) -> str:
        """Build strategy prompt with accumulated context"""
        
        ticket = state["ticket_info"]
        requirements = state["extracted_requirements"]
        modules = state["impacted_modules"]
        dependencies = state["dependencies"]
        risks = state["risk_areas"]
        
        return f"""Create a comprehensive QA roadmap for this change.

**Ticket:** {ticket.get('ticket_id', 'Unknown')} - {ticket.get('title', '')}
**Type:** {ticket.get('ticket_type', 'Unknown')}
**Priority:** {ticket.get('priority', 'Unknown')}

**Requirements:**
{chr(10).join(f"- {req}" for req in requirements)}

**Impacted Modules:**
{chr(10).join(f"- {mod}" for mod in modules)}

**Dependencies:**
{chr(10).join(f"- {dep}" for dep in dependencies)}

**Risk Areas:**
{chr(10).join(f"- {risk}" for risk in risks)}

Create a detailed QA roadmap organized by test categories."""
