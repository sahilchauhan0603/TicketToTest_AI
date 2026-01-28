"""
Context Builder Agent
Understands impacted modules, dependencies, and system context
"""
from typing import Dict, List
import json
import google.generativeai as genai
from agents.state import AgentState, log_agent_action
import os


class ContextBuilderAgent:
    """
    Agent that builds context about what parts of the system are impacted
    and what dependencies exist
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "ContextBuilderAgent"
    
    def process(self, state: AgentState) -> AgentState:
        """
        Identify impacted modules and dependencies
        """
        state["current_agent"] = self.name
        
        # Build prompt with previous agent's output
        prompt = self._build_context_prompt(state)
        
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
        state["impacted_modules"] = result.get("impacted_modules", [])
        state["dependencies"] = result.get("dependencies", [])
        state["risk_areas"] = result.get("risk_areas", [])
        
        # Log action
        log_agent_action(state, self.name, "identified_context", {
            "modules_count": len(state["impacted_modules"]),
            "dependencies_count": len(state["dependencies"]),
            "risk_areas_count": len(state["risk_areas"])
        })
        
        return state
    
    def _get_system_prompt(self) -> str:
        return """You are an expert system architect and QA strategist.

Your task is to:
1. Identify all system modules/components impacted by this change
2. Map out dependencies (APIs, databases, third-party services, UI components)
3. Highlight risk areas that need extra testing attention

Return a JSON object with:
{
    "impacted_modules": ["module1", "module2", ...],
    "dependencies": ["dependency1", "dependency2", ...],
    "risk_areas": ["risk1", "risk2", ...]
}

Think about:
- Frontend vs Backend impacts
- Database schema changes
- API contract changes
- Authentication/Authorization impacts
- Integration points
- Data migration needs"""
    
    def _build_context_prompt(self, state: AgentState) -> str:
        """Build prompt with ticket and extracted requirements"""
        
        ticket = state["ticket_info"]
        requirements = state["extracted_requirements"]
        
        return f"""Analyze the system context and impacts for this change.

**Ticket Type:** {ticket.get('ticket_type', 'Unknown')}
**Title:** {ticket.get('title', '')}
**Priority:** {ticket.get('priority', 'Unknown')}

**Extracted Requirements:**
{chr(10).join(f"- {req}" for req in requirements)}

**Linked Tickets:** {', '.join(ticket.get('linked_tickets', [])) or 'None'}

Identify all impacted modules, dependencies, and risk areas."""
