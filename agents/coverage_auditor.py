"""
Coverage Auditor Agent
Reviews generated test cases and identifies coverage gaps
"""
from typing import Dict, List
import json
import google.generativeai as genai
from agents.state import AgentState, log_agent_action
import os


class CoverageAuditorAgent:
    """
    Agent that audits test coverage and identifies gaps
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "CoverageAuditorAgent"
    
    def process(self, state: AgentState) -> AgentState:
        """
        Audit test coverage and identify gaps
        """
        state["current_agent"] = self.name
        
        # Build audit prompt
        prompt = self._build_audit_prompt(state)
        
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
        state["coverage_gaps"] = result.get("coverage_gaps", [])
        
        # Add any additional clarification questions
        if result.get("additional_questions"):
            state["clarification_questions"].extend(result["additional_questions"])
        
        # Log action
        log_agent_action(state, self.name, "audited_coverage", {
            "gaps_found": len(state["coverage_gaps"]),
            "coverage_score": result.get("coverage_score", "N/A")
        })
        
        return state
    
    def _get_system_prompt(self) -> str:
        return """You are an expert QA auditor who reviews test coverage for completeness.

Your task is to:
1. Review all generated test cases against requirements
2. Identify coverage gaps (untested scenarios, edge cases, error conditions)
3. Rate overall coverage quality
4. Suggest additional test scenarios if needed

Return JSON:
{
    "coverage_gaps": ["gap1", "gap2", ...],
    "coverage_score": "Excellent/Good/Fair/Poor",
    "additional_questions": ["question1", "question2", ...] (optional),
    "recommendations": ["recommendation1", ...] (optional)
}

Look for:
- Untested requirements
- Missing error scenarios
- Boundary conditions not covered
- Integration scenarios missed
- Security/performance considerations
- Data validation gaps"""
    
    def _build_audit_prompt(self, state: AgentState) -> str:
        """Build audit prompt with all generated artifacts"""
        
        ticket = state["ticket_info"]
        requirements = state["extracted_requirements"]
        test_cases = state["test_cases"]
        
        # Summarize test cases by category
        tc_summary = {}
        for tc in test_cases:
            category = tc.get("category", "Other")
            tc_summary[category] = tc_summary.get(category, 0) + 1
        
        return f"""Audit the test coverage for this ticket.

**Ticket:** {ticket.get('ticket_id')} - {ticket.get('title')}
**Type:** {ticket.get('ticket_type')}
**Priority:** {ticket.get('priority')}

**Requirements to Cover:**
{chr(10).join(f"- {req}" for req in requirements)}

**Test Cases Generated:**
Total: {len(test_cases)} test cases
{chr(10).join(f"- {cat}: {count} test cases" for cat, count in tc_summary.items())}

**Sample Test Case Titles:**
{chr(10).join(f"- [{tc.get('priority')}] {tc.get('title')}" for tc in test_cases[:15])}
{"... and more" if len(test_cases) > 15 else ""}

**Risk Areas Identified:**
{chr(10).join(f"- {risk}" for risk in state.get('risk_areas', []))}

Review coverage and identify any gaps."""
