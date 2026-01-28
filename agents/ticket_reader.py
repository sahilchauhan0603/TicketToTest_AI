"""
Ticket Reader Agent
Extracts key requirements, acceptance criteria, and metadata from tickets
"""
from typing import Dict, List
import json
import google.generativeai as genai
from agents.state import AgentState, log_agent_action
import os


class TicketReaderAgent:
    """
    Agent responsible for understanding the ticket and extracting structured information
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "TicketReaderAgent"
    
    def process(self, state: AgentState) -> AgentState:
        """
        Extract requirements and identify gaps in acceptance criteria
        """
        state["current_agent"] = self.name
        
        ticket = state["ticket_info"]
        
        # Build prompt for extraction
        prompt = self._build_extraction_prompt(ticket)
        
        # Call Gemini with structured output
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
        
        # Parse response
        result = json.loads(response.text)
        
        # Update state
        state["extracted_requirements"] = result.get("requirements", [])
        state["acceptance_criteria_gaps"] = result.get("ac_gaps", [])
        state["clarification_questions"] = result.get("clarification_questions", [])
        
        # Log action
        log_agent_action(state, self.name, "extracted_requirements", {
            "requirements_count": len(state["extracted_requirements"]),
            "gaps_found": len(state["acceptance_criteria_gaps"])
        })
        
        return state
    
    def _get_system_prompt(self) -> str:
        return """You are an expert QA analyst specializing in requirement extraction.
        
Your task is to:
1. Extract all testable requirements from the ticket
2. Identify missing or ambiguous acceptance criteria
3. Generate clarifying questions for unclear requirements

Return a JSON object with:
{
    "requirements": ["requirement 1", "requirement 2", ...],
    "ac_gaps": ["gap 1", "gap 2", ...],
    "clarification_questions": ["question 1", "question 2", ...]
}

Be thorough and look for edge cases and implicit requirements."""
    
    def _build_extraction_prompt(self, ticket: Dict) -> str:
        """Build the prompt from ticket information"""
        
        ac_section = ""
        if ticket.get("acceptance_criteria"):
            ac_section = f"\n**Acceptance Criteria:**\n" + "\n".join(
                f"- {ac}" for ac in ticket["acceptance_criteria"]
            )
        
        comments_section = ""
        if ticket.get("comments"):
            comments_section = f"\n**Recent Comments:**\n" + "\n".join(
                f"- {c.get('author', 'Unknown')}: {c.get('body', '')}" 
                for c in ticket["comments"][:5]  # Last 5 comments
            )
        
        return f"""Analyze this {ticket.get('ticket_type', 'ticket')} and extract all testable requirements.

**Ticket ID:** {ticket.get('ticket_id', 'Unknown')}
**Title:** {ticket.get('title', 'No title')}
**Priority:** {ticket.get('priority', 'Unknown')}
**Status:** {ticket.get('status', 'Unknown')}

**Description:**
{ticket.get('description', 'No description provided')}
{ac_section}
{comments_section}

**Attachments:** {', '.join(ticket.get('attachments', [])) or 'None'}
**Linked Tickets:** {', '.join(ticket.get('linked_tickets', [])) or 'None'}

Extract all requirements and identify gaps in acceptance criteria."""
