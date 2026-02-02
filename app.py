"""
Ticket-to-Test AI - Streamlit Demo Application
"""
import streamlit as st
import os
from dotenv import load_dotenv
import time
from pathlib import Path
import json
import google.generativeai as genai

from agents.orchestrator import AgentOrchestrator
from agents.state import TicketInfo
from utils.excel_exporter import ExcelExporter
from utils.sample_tickets import get_sample_ticket, SAMPLE_TICKETS

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Ticket-to-Test AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Theme with Dark Mode Support
st.markdown("""
<style>
    /* Light Theme (Default) */
    .main {
        background-color: #f8f9fa;
        padding-top: 3rem !important;
    }
    
    .block-container {
        padding-top: 3rem !important;
    }
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
        margin-top: 0;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .sub-header {
        color: #5f6368;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 0rem;
        line-height: 0.5;
    }
    
    /* Dark Theme Overrides */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #0e1117;
        }
        
        .main-header {
            color: #fafafa;
        }
        
        .sub-header {
            color: #a0a0a0;
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1d24 0%, #0e1117 100%) !important;
            border-right: 1px solid #262730 !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: #fafafa !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: #fafafa !important;
        }
        
        section[data-testid="stSidebar"] label {
            color: #fafafa !important;
        }
        
        /* Sidebar Header Dark Mode */
        .sidebar-header {
            border-bottom-color: #4a9eff !important;
        }
        
        .sidebar-header-icon {
            color: #4a9eff !important;
        }
        
        .sidebar-header-title {
            color: #fafafa !important;
        }
        
        /* Pipeline Box Dark Mode */
        .pipeline-box {
            background-color: #1a1d24 !important;
            border-color: #3d4046 !important;
        }
        
        .pipeline-title {
            color: #fafafa !important;
        }
        
        .pipeline-item {
            color: #a0a0a0 !important;
        }
        
        section[data-testid="stSidebar"] .stTextInput input {
            background-color: #262730 !important;
            border: 1px solid #3d4046 !important;
            color: #fafafa !important;
        }
        
        section[data-testid="stSidebar"] .stTextInput input:focus {
            border-color: #4a9eff !important;
            box-shadow: 0 0 0 1px #4a9eff !important;
            background-color: #1a1d24 !important;
        }
        
        .stTextArea textarea {
            background-color: #1a1d24 !important;
            border: 1px solid #3d4046 !important;
            color: #e0e0e0 !important;
        }
        
        .stTextArea textarea:focus {
            border-color: #4a9eff !important;
            box-shadow: 0 0 0 1px #4a9eff !important;
            background-color: #262730 !important;
        }
        
        .stTextArea textarea:disabled {
            background-color: #1a1d24 !important;
            color: #808080 !important;
        }
        
        .stExpander {
            border: 1px solid #3d4046 !important;
        }
        
        hr {
            border-color: #3d4046 !important;
        }
        
        section[data-testid="stSidebar"] div[data-testid="stMetric"] {
            background-color: #1a1d24 !important;
            border: 1px solid #3d4046 !important;
        }
        
        div[data-testid="stMetricValue"] {
            color: #4a9eff !important;
        }
    }
    
    /* Common Styles for Both Themes */
    .stExpander {
        border-radius: 4px;
        margin-bottom: 0.5rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1967d2;
    }
    
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
        letter-spacing: 0.3px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button[kind="primary"] {
        padding: 0.5rem 2rem;
        font-size: 0.95rem;
        min-height: 2.5rem;
    }
    
    /* Sidebar - Light Theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid #e0e0e0;
        padding-top: 1rem !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] label {
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] .stTextInput input {
        border-radius: 4px;
        border: 1px solid #dadce0;
        padding: 0.5rem 0.75rem;
        font-size: 0.9rem;
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #1967d2;
        box-shadow: 0 0 0 1px #1967d2;
    }
    
    /* Text Areas - Light Theme */
    .stTextArea textarea {
        border-radius: 4px;
        border: 1px solid #dadce0;
        padding: 0.75rem;
        font-size: 0.9rem;
        font-family: 'Segoe UI', system-ui, monospace;
        line-height: 1.6;
        background-color: #fafafa;
    }
    
    .stTextArea textarea:focus {
        border-color: #1967d2;
        box-shadow: 0 0 0 1px #1967d2;
        background-color: #ffffff;
    }
    
    .stTextArea textarea:disabled {
        background-color: #f5f5f5;
        color: #5f6368;
    }
    
    .stAlert {
        border-radius: 4px;
        border-left: 4px solid;
        font-size: 0.9rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    hr {
        margin: 1.5rem 0;
        border-color: #e0e0e0;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stMetricValue"] {
        font-size: 1.3rem;
        color: #1967d2;
    }
    
    /* Sidebar Custom Elements - Light Theme */
    .sidebar-header {
        padding: 0rem 0 1.5rem 0;
        text-align: center;
        border-bottom: 2px solid #1967d2;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-header-icon {
        color: #1967d2;
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    
    .sidebar-header-title {
        margin: 0;
        color: #1a1a1a;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .pipeline-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .pipeline-title {
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #1a1a1a;
    }
    
    .pipeline-item {
        font-size: 0.85rem;
        line-height: 2;
        color: #5f6368;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'final_state' not in st.session_state:
        st.session_state.final_state = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def display_header():
    """Display application header"""
    st.markdown('<p class="main-header">Ticket-to-Test AI Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Test Case Generation & Quality Assurance Automation</p>', unsafe_allow_html=True)
    
    # Feature highlights section
    st.markdown("---")
    st.markdown("### 🎯 Platform Capabilities")
    st.caption("Transform tickets into comprehensive test suites with intelligent AI agents")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**📋 QA Roadmap**")
        st.caption("Strategic test planning")
    with col2:
        st.markdown("**✅ Test Cases**")
        st.caption("Structured & detailed")
    with col3:
        st.markdown("**🔍 Coverage Analysis**")
        st.caption("Gap identification")
    with col4:
        st.markdown("**📊 Excel Export**")
        st.caption("Professional format")


def display_sidebar():
    """Display sidebar with configuration"""
    with st.sidebar:
        # Professional Header
        st.markdown("""
        <div class='sidebar-header'>
            <h2 class='sidebar-header-title'>Configuration</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # API Settings Section
        st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("**API Credentials**")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
            help="Enter your Google Gemini API key"
        )
        
        # Rate limit configuration
        with st.expander("⏱️ Rate Limit Settings", expanded=False):
            st.markdown("**Free Tier Limits (Gemini Flash)**")
            st.caption("• 5 requests per minute (RPM)")
            st.caption("• Each ticket uses 5 API calls (one per agent)")
            st.caption("• System auto-pauses to respect limits")
            
            # Cache settings
            st.markdown("**Optimization Settings**")
            enable_cache = st.checkbox("Enable Response Caching", value=True, 
                                      help="Cache API responses to avoid redundant calls")
            if enable_cache:
                st.caption("✅ Enabled - Identical requests use cached responses")
            else:
                st.caption("⚠️ Disabled - Every request will use an API call")
        
        # Update environment
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Processing Pipeline
        st.markdown("""
        <div class='pipeline-box'>
            <div class='pipeline-title'>Processing Pipeline - 5-step workflow that the AI agents follows</div>
            <div class='pipeline-item'>
                <div>1. Ticket Analysis</div>
                <div>2. Context Building</div>
                <div>3. Strategy Design</div>
                <div>4. Test Generation</div>
                <div>5. Coverage Audit</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Session Statistics
        st.markdown("**Session Statistics**")
        col1, col2 = st.columns(2)
        
        # Calculate real metrics from session state
        if st.session_state.final_state:
            num_test_cases = len(st.session_state.final_state.get('test_cases', []))
            processing_time = st.session_state.final_state.get('processing_time', 0)
            
            with col1:
                st.metric("Test Cases", num_test_cases, help="Total test cases generated")
            with col2:
                st.metric("Time", f"{processing_time:.1f}s", help="Processing time")
        else:
            with col1:
                st.metric("Test Cases", "-", help="No session active")
            with col2:
                st.metric("Time", "-", help="No session active")


def generate_ticket_details(title: str, ticket_type: str) -> dict:
    """
    Generate description and acceptance criteria using AI based on title
    
    Args:
        title: The ticket title
        ticket_type: Type of ticket (bug, story, task)
    
    Returns:
        Dictionary with 'description' and 'acceptance_criteria' keys
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"))
        
        prompt = f"""You are a technical product manager. Given a ticket title and type, generate a detailed description and acceptance criteria.

Ticket Type: {ticket_type}
Ticket Title: {title}

Generate:
1. A detailed description (2-3 paragraphs) that includes:
   - What needs to be done
   - Context and background
   - Technical considerations (if applicable)
   - Expected behavior

2. 4-6 clear and testable acceptance criteria

Format your response as JSON:
{{
    "description": "detailed description here",
    "acceptance_criteria": [
        "criterion 1",
        "criterion 2",
        "criterion 3"
    ]
}}

Keep it professional and specific to the ticket type."""

        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        result = json.loads(response_text.strip())
        return result
    
    except Exception as e:
        st.error(f"Error generating details: {str(e)}")
        return None


def display_ticket_input():
    """Display ticket input section"""
    st.markdown("### Step 1: Ticket Input")
    st.caption("Select or import a ticket to begin test case generation")
    
    # Initialize selected ticket in session state
    if 'selected_ticket' not in st.session_state:
        st.session_state.selected_ticket = None
    
    # Tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Sample Tickets", "Live Integration", "Custom Input"])
    
    with tab1:
        st.markdown("**Select a demonstration ticket:**")
        
        sample_type = st.selectbox(
            "Choose sample ticket type:",
            ["bug_fix", "feature", "api_change"],
            format_func=lambda x: {
                "bug_fix": "🐛 Bug Fix - Login with Special Characters",
                "feature": "✨ Feature - PDF Export for Reports",
                "api_change": "🔧 API Change - Profile Picture Upload"
            }[x]
        )
        
        ticket = get_sample_ticket(sample_type)
        
        # Display ticket preview
        with st.expander("📄 View Ticket Details", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**ID:** {ticket['ticket_id']}")
                st.markdown(f"**Type:** {ticket['ticket_type']}")
            with col2:
                st.markdown(f"**Priority:** {ticket['priority']}")
                st.markdown(f"**Status:** {ticket['status']}")
            with col3:
                st.markdown(f"**Attachments:** {len(ticket['attachments'])}")
                st.markdown(f"**Comments:** {len(ticket['comments'])}")
            
            st.markdown("<p style='font-weight: 600; text-decoration: underline;'>Title:</p>", unsafe_allow_html=True)
            st.info(ticket['title'])
            
            st.markdown("<p style='font-weight: 600; text-decoration: underline;'>Description:</p>", unsafe_allow_html=True)
            st.text_area("", ticket['description'], height=150, disabled=True, label_visibility="collapsed", key="sample_desc")
            
            if ticket['acceptance_criteria']:
                st.markdown("<p style='font-weight: 600; text-decoration: underline;'>Acceptance Criteria:</p>", unsafe_allow_html=True)
                for ac in ticket['acceptance_criteria']:
                    st.markdown(f"- {ac}")
            
            # Display attachments if any
            if ticket['attachments']:
                st.markdown("<p style='font-weight: 600; text-decoration: underline;'>Attachments:</p>", unsafe_allow_html=True)
                for attachment in ticket['attachments']:
                    st.markdown(f"📎 {attachment}")
            
            # Display comments if any
            if ticket['comments']:
                st.markdown("<p style='font-weight: 600; text-decoration: underline;'>Comments:</p>", unsafe_allow_html=True)
                for comment in ticket['comments']:
                    with st.container():
                        st.markdown(f"**{comment['author']}:**")
                        st.markdown(f"> {comment['body']}")
                        st.markdown("")
        
        # Store ticket for this tab
        st.session_state.selected_ticket = ticket
    
    with tab2:
        st.markdown("**Fetch tickets directly from Jira or Azure DevOps:**")
        
        from integrations.manager import IntegrationManager
        manager = IntegrationManager()
        
        # Integration selection
        col1, col2 = st.columns(2)
        
        with col1:
            integration_type = st.selectbox(
                "Select Integration",
                ["Jira", "Azure DevOps"],
                help="Choose your ticket management system"
            )
        
        with col2:
            # Check if configured
            is_configured = manager.is_configured(integration_type.lower().replace(' ', '_'))
            if is_configured:
                st.success(f"✓ {integration_type} configured")
            else:
                st.warning(f"⚠ {integration_type} not configured")
        
        # Configuration instructions
        if not is_configured:
            with st.expander("⚙️ Setup Instructions", expanded=False):
                if integration_type == "Jira":
                    st.markdown("""
                    **Configure Jira in .env file:**
                    ```
                    JIRA_URL=https://your-domain.atlassian.net
                    JIRA_EMAIL=your-email@example.com
                    JIRA_API_TOKEN=your_api_token
                    ```
                    
                    **Get API Token:**
                    1. Go to https://id.atlassian.com/manage/api-tokens
                    2. Create API token
                    3. Copy and paste into .env
                    """)
                else:
                    st.markdown("""
                    **Configure Azure DevOps in .env file:**
                    ```
                    AZURE_DEVOPS_ORG=https://dev.azure.com/your-org
                    AZURE_DEVOPS_PAT=your_personal_access_token
                    AZURE_DEVOPS_PROJECT=your-project-name
                    ```
                    
                    **Get Personal Access Token:**
                    1. Go to Azure DevOps → User Settings → Personal Access Tokens
                    2. Create new token with Work Items (Read & Write)
                    3. Copy and paste into .env
                    """)
        
        # Ticket ID input
        ticket_id = st.text_input(
            "Ticket ID",
            placeholder="PROJ-123" if integration_type == "Jira" else "12345",
            help=f"Enter the {integration_type} ticket/work item ID"
        )
        
        # Fetch button
        if st.button("🔍 Fetch Ticket", type="secondary", disabled=not is_configured):
            if not ticket_id:
                st.error("Please enter a ticket ID")
            else:
                with st.spinner(f"Fetching ticket from {integration_type}..."):
                    integration = manager.get_integration(integration_type.lower().replace(' ', '_'))
                    
                    if integration:
                        ticket = integration.fetch_ticket(ticket_id)
                        
                        if ticket:
                            st.success(f"✓ Successfully fetched {ticket_id}")
                            
                            # Display ticket preview
                            with st.expander("📄 Ticket Details", expanded=True):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"**ID:** {ticket['ticket_id']}")
                                    st.markdown(f"**Type:** {ticket['ticket_type']}")
                                with col2:
                                    st.markdown(f"**Priority:** {ticket['priority']}")
                                    st.markdown(f"**Status:** {ticket['status']}")
                                with col3:
                                    st.markdown(f"**Attachments:** {len(ticket['attachments'])}")
                                    st.markdown(f"**Comments:** {len(ticket['comments'])}")
                                
                                st.markdown("**Title:**")
                                st.info(ticket['title'])
                                
                                st.markdown("**Description:**")
                                st.text_area("", ticket['description'], height=150, disabled=True, label_visibility="collapsed")
                                
                                if ticket['acceptance_criteria']:
                                    st.markdown("**Acceptance Criteria:**")
                                    for ac in ticket['acceptance_criteria']:
                                        st.markdown(f"- {ac}")
                            
                            st.session_state.selected_ticket = ticket
                        else:
                            st.error(f"Failed to fetch ticket {ticket_id}. Check the ID and try again.")
                    else:
                        st.error(f"Failed to connect to {integration_type}. Check your credentials in .env")
    
    with tab3:
        st.markdown("**Enter your own ticket details:**")
        
        col1, col2 = st.columns(2)
        with col1:
            ticket_id = st.text_input("Ticket ID", value="CUSTOM-001", key="custom_ticket_id")
            ticket_type = st.selectbox("Type", ["bug", "story", "task"], key="custom_type")
            priority = st.selectbox("Priority", ["P0", "P1", "P2", "P3"], key="custom_priority")
        
        with col2:
            title = st.text_input("Title", placeholder="Enter ticket title...", key="custom_title")
            status = st.selectbox("Status", ["To Do", "In Progress", "In Review"], key="custom_status")
        
        # AI Generation Feature
        if title:
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn2:
                if st.button("✨ AI Generate", type="secondary", help="Auto-generate description and acceptance criteria using AI"):
                    if not os.getenv("GOOGLE_API_KEY"):
                        st.error("⚠️ Please enter your Google Gemini API key in the sidebar.")
                    else:
                        with st.spinner("🤖 AI is generating ticket details..."):
                            result = generate_ticket_details(title, ticket_type)
                            if result:
                                # Update session state with widget keys so content appears in text areas
                                st.session_state.custom_description = result.get('description', '')
                                st.session_state.custom_ac = '\n'.join(result.get('acceptance_criteria', []))
                                st.success("✅ Details generated! You can edit them below.")
                                st.rerun()
        
        description = st.text_area(
            "Description", 
            height=150, 
            placeholder="Describe the ticket in detail...\n\nInclude:\n- What needs to be done\n- Expected behavior\n- Any technical details\n\n💡 Tip: Enter a title and click 'AI Generate' to auto-fill this field!",
            key="custom_description"
        )
        
        ac_input = st.text_area(
            "Acceptance Criteria (one per line)",
            height=100,
            placeholder="Given a user is logged in\nWhen they click the submit button\nThen the form should be saved\n\n💡 Tip: Use 'AI Generate' button above to auto-fill!",
            help="Enter each acceptance criterion on a new line",
            key="custom_ac"
        )
        
        acceptance_criteria = [ac.strip() for ac in ac_input.split('\n') if ac.strip()]
        
        # Build the custom ticket dictionary
        custom_ticket: TicketInfo = {
            'ticket_id': ticket_id,
            'title': title,
            'description': description,
            'acceptance_criteria': acceptance_criteria,
            'ticket_type': ticket_type,
            'priority': priority,
            'status': status,
            'attachments': [],
            'comments': [],
            'linked_tickets': []
        }
        
        # Preview section
        if title or description:
            with st.expander("📄 Preview Custom Ticket", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**ID:** {ticket_id}")
                    st.markdown(f"**Type:** {ticket_type}")
                with col2:
                    st.markdown(f"**Priority:** {priority}")
                    st.markdown(f"**Status:** {status}")
                with col3:
                    st.markdown(f"**Acceptance Criteria:** {len(acceptance_criteria)}")
                
                if title:
                    st.markdown("**Title:**")
                    st.info(title)
                
                if description:
                    st.markdown("**Description:**")
                    st.text_area("", description, height=100, disabled=True, label_visibility="collapsed", key="preview_desc")
                
                if acceptance_criteria:
                    st.markdown("**Acceptance Criteria:**")
                    for ac in acceptance_criteria:
                        st.markdown(f"- {ac}")
        
        # Validation
        if not title:
            st.warning("⚠️ Please enter a ticket title to proceed.")
        if not description:
            st.warning("⚠️ Please enter a description to proceed.")
        
        # Store valid ticket
        if title and description:
            st.session_state.selected_ticket = custom_ticket
    
    # Return the selected ticket from session state
    return st.session_state.selected_ticket


def process_ticket(ticket: TicketInfo):
    """Process ticket through agent pipeline"""
    st.markdown("### Step 2: AI Processing")
    st.caption("Multi-agent system analyzes ticket and generates comprehensive test cases")
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ Please enter your Google Gemini API key in the sidebar to continue.")
        return None
    
    # Initialize orchestrator
    if st.session_state.orchestrator is None:
        with st.spinner("Initializing agent orchestrator..."):
            st.session_state.orchestrator = AgentOrchestrator(os.getenv("GOOGLE_API_KEY"))
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Test Cases", type="primary", use_container_width=True)
    
    if generate_btn:
        st.session_state.processing = True
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        wait_text = st.empty()  # For rate limit wait times
        agent_logs = st.container()
        
        agents = [
            "ticket_reader",
            "context_builder", 
            "test_strategy",
            "test_generator",
            "coverage_auditor"
        ]
        
        agent_names = {
            "ticket_reader": "📖 Ticket Reader Agent",
            "context_builder": "🏗️ Context Builder Agent",
            "test_strategy": "🎯 Test Strategy Agent",
            "test_generator": "✏️ Test Generator Agent",
            "coverage_auditor": "🔍 Coverage Auditor Agent"
        }
        
        # Counter for agent execution
        current_agent_idx = [0]
        
        def progress_callback(agent_name: str, state):
            if agent_name in agents:
                idx = agents.index(agent_name)
                progress = (idx + 1) / len(agents)
                progress_bar.progress(progress)
                status_text.markdown(f"**Processing:** {agent_names.get(agent_name, agent_name)}")
                wait_text.empty()  # Clear wait message
                
                with agent_logs:
                    with st.expander(f"✅ {agent_names.get(agent_name, agent_name)}", expanded=False):
                        if agent_name == "ticket_reader":
                            st.write(f"Requirements extracted: {len(state.get('extracted_requirements', []))}")
                            st.write(f"Gaps found: {len(state.get('acceptance_criteria_gaps', []))}")
                        elif agent_name == "context_builder":
                            st.write(f"Impacted modules: {len(state.get('impacted_modules', []))}")
                            st.write(f"Dependencies: {len(state.get('dependencies', []))}")
                        elif agent_name == "test_strategy":
                            roadmap = state.get('qa_roadmap', {})
                            st.write(f"Test categories: {len(roadmap)}")
                        elif agent_name == "test_generator":
                            st.write(f"Test cases generated: {len(state.get('test_cases', []))}")
                        elif agent_name == "coverage_auditor":
                            st.write(f"Coverage gaps: {len(state.get('coverage_gaps', []))}")
        
        # Show info about rate limits
        rate_info = st.info("⏱️ **Note**: Using free tier limits (5 API calls/minute). System will pause ~12 seconds between agents to respect rate limits.")
        
        # Process ticket
        try:
            final_state = st.session_state.orchestrator.process_ticket(
                ticket,
                progress_callback=progress_callback
            )
            
            st.session_state.final_state = final_state
            st.session_state.processing = False
            
            progress_bar.progress(1.0)
            status_text.markdown("**✅ Processing Complete!**")
            wait_text.empty()
            
            st.success(f"✅ Generated {len(final_state['test_cases'])} test cases in {final_state['processing_time']:.2f} seconds!")
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.session_state.processing = False
            return None
    
    return st.session_state.final_state


def display_results(state):
    """Display results and outputs"""
    if state is None:
        return
    
    st.markdown("### Step 3: Generated Outputs")
    st.caption("Review test cases, coverage analysis, and export options")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Test Cases Generated",
            len(state['test_cases']),
            help="Total number of test cases created"
        )
    
    with col2:
        priority_counts = {}
        for tc in state['test_cases']:
            p = tc.get('priority', 'P2')
            priority_counts[p] = priority_counts.get(p, 0) + 1
        st.metric(
            "P0/P1 Cases",
            priority_counts.get('P0', 0) + priority_counts.get('P1', 0),
            help="High priority test cases"
        )
    
    with col3:
        st.metric(
            "Coverage Gaps",
            len(state.get('coverage_gaps', [])),
            help="Coverage gaps identified"
        )
    
    with col4:
        categories = set(tc.get('category', 'Other') for tc in state['test_cases'])
        st.metric(
            "Test Categories",
            len(categories),
            help="Different test categories"
        )
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["QA Roadmap", "Test Cases", "Coverage Analysis", "Export & Sync"])
    
    with tab1:
        st.subheader("QA Roadmap by Category")
        
        roadmap = state.get('qa_roadmap', {})
        for category, items in roadmap.items():
            with st.expander(f"📂 {category}", expanded=True):
                for item in items:
                    st.markdown(f"- {item}")
    
    with tab2:
        st.subheader("Generated Test Cases")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Priority filter
            priorities = sorted(set(tc.get('priority', 'P2') for tc in state['test_cases']), reverse=True)
            priority_filter = st.multiselect(
                "Filter by Priority",
                priorities,
                default=priorities
            )
        
        with col2:
            # Category filter
            categories = sorted(set(tc.get('category', 'Other') for tc in state['test_cases']))
            category_filter = st.multiselect(
                "Filter by Category",
                categories,
                default=categories
            )
        
        # Display test cases
        filtered_cases = [
            tc for tc in state['test_cases']
            if tc.get('priority') in priority_filter and tc.get('category') in category_filter
        ]
        
        for tc in filtered_cases:
            priority_color = {
                "P0": "🔴",
                "P1": "🟠",
                "P2": "🟡",
                "P3": "🟢"
            }.get(tc.get('priority', 'P2'), '🔵')
            
            with st.expander(f"{priority_color} [{tc.get('test_id')}] {tc.get('title')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Category:** {tc.get('category')}")
                    st.markdown(f"**Priority:** {tc.get('priority')}")
                    st.markdown(f"**Preconditions:** {tc.get('preconditions')}")
                    
                    st.markdown("**Test Steps:**")
                    for i, step in enumerate(tc.get('test_steps', []), 1):
                        st.markdown(f"{i}. {step}")
                    
                    st.markdown(f"**Expected Result:** {tc.get('expected_result')}")
                    
                    if tc.get('test_data'):
                        st.markdown(f"**Test Data:** {tc.get('test_data')}")
                
                with col2:
                    st.markdown(f"**Automation:**")
                    st.markdown(tc.get('automation_feasibility', 'Medium'))
    
    with tab3:
        st.subheader("Coverage Analysis")
        
        # Coverage gaps
        gaps = state.get('coverage_gaps', [])
        if gaps:
            st.markdown("### ⚠️ Coverage Gaps Identified")
            for gap in gaps:
                st.warning(gap)
        else:
            st.success("✅ Excellent coverage! No gaps identified.")
        
        st.divider()
        
        # Clarification questions
        questions = state.get('clarification_questions', [])
        if questions:
            st.markdown("### ❓ Clarification Questions")
            for q in questions:
                st.info(q)
        
        st.divider()
        
        # Risk areas
        risks = state.get('risk_areas', [])
        if risks:
            st.markdown("### ⚡ Risk Areas")
            for risk in risks:
                st.markdown(f"- {risk}")
    
    with tab4:
        st.subheader("Export & Sync")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Download Excel")
            st.markdown("""
            Download test cases in Excel format:
            - Summary with statistics
            - Detailed test cases
            - QA roadmap by category
            - Coverage analysis
            """)
            
            # Export button
            if st.button("📥 Generate Excel File", type="primary"):
                with st.spinner("Generating Excel file..."):
                    # Create output directory
                    output_dir = Path("outputs")
                    output_dir.mkdir(exist_ok=True)
                    
                    # Generate filename
                    ticket_id = state['ticket_info']['ticket_id'].replace('/', '_')
                    filename = f"TestCases_{ticket_id}_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
                    output_path = output_dir / filename
                    
                    # Export
                    exporter = ExcelExporter()
                    exporter.export_test_cases(state, str(output_path))
                    
                    # Store path in session for sync
                    st.session_state.excel_path = str(output_path)
                    
                    # Download button
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Excel File",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success(f"✅ Excel file generated: {filename}")
        
        with col2:
            st.markdown("### 🔄 Sync to Jira/Azure DevOps")
            
            from integrations.manager import IntegrationManager
            manager = IntegrationManager()
            
            # Check if any integration is configured
            jira_configured = manager.is_configured('jira')
            ado_configured = manager.is_configured('azure_devops')
            
            if not (jira_configured or ado_configured):
                st.info("⚠️ Configure Jira or Azure DevOps in .env to sync results back")
            else:
                sync_options = []
                
                st.markdown("**Sync options:**")
                
                post_comment = st.checkbox("Post summary comment", value=True)
                attach_file = st.checkbox("Attach Excel file", value=False)
                create_subtasks = st.checkbox("Create test subtasks/tasks", value=False)
                
                if st.button("🔄 Sync to Ticket System", type="secondary"):
                    with st.spinner("Syncing to ticket system..."):
                        try:
                            from agents.sync_agent import SyncAgent
                            
                            # Ensure Excel is generated if attaching
                            excel_path = st.session_state.get('excel_path')
                            if attach_file and not excel_path:
                                # Generate Excel first
                                output_dir = Path("outputs")
                                output_dir.mkdir(exist_ok=True)
                                ticket_id = state['ticket_info']['ticket_id'].replace('/', '_')
                                filename = f"TestCases_{ticket_id}_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
                                excel_path = str(output_dir / filename)
                                exporter = ExcelExporter()
                                exporter.export_test_cases(state, excel_path)
                            
                            sync_agent = SyncAgent()
                            sync_options = {
                                'post_comment': post_comment,
                                'attach_file': attach_file,
                                'excel_path': excel_path,
                                'create_subtasks': create_subtasks
                            }
                            
                            state_copy = dict(state)
                            _, sync_result = sync_agent.process(state_copy, sync_options)
                            
                            # Display results
                            if sync_result["success"]:
                                st.success(f"✅ {sync_result['message']}")
                                for detail in sync_result["details"]:
                                    st.write(detail)
                                st.balloons()
                            else:
                                st.warning(f"⚠️ {sync_result['message']}")
                                for detail in sync_result["details"]:
                                    st.write(detail)
                        
                        except Exception as e:
                            st.error(f"❌ Failed to sync: {str(e)}")
                            st.error("Please check your .env configuration and ensure Jira/Azure DevOps credentials are correct.")


def main():
    """Main application"""
    init_session_state()
    display_header()
    display_sidebar()
    
    st.divider()
    
    # Step 1: Ticket Input
    ticket = display_ticket_input()
    
    st.divider()
    
    # Step 2: Processing
    if ticket:
        final_state = process_ticket(ticket)
        
        st.divider()
        
        # Step 3: Results
        if final_state:
            display_results(final_state)


if __name__ == "__main__":
    main()
