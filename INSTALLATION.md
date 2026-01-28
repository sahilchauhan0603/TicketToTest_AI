# Installation & Deployment Guide

## Quick Start (5 Minutes)

### Prerequisites
- **Python 3.11 or higher**
- Google Gemini API key (get from https://makersuite.google.com/app/apikey)

**Check your Python version:**
```powershell
python --version
```

### Installation Steps

1. **Navigate to project**
   ```powershell
   cd c:\THIS_DEVICE\VS_Code\PROJECTS\TicketToTest_AI
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv venv          # Creating venv
   .\venv\Scripts\Activate.ps1  # Activate venv -> On Windows
   ```
   
   **⚠️ Important:** Make sure you see `(venv)` at the start of your prompt before continuing!

3. **Install dependencies** (only after venv is activated)
   ```powershell
   # Verify venv is active first:
   Get-Command python | Select-Object Source
   # Should show: ...\venv\Scripts\python.exe
   
   # Then install:
   pip install streamlit google-generativeai langchain langgraph python-dotenv openpyxl pandas requests jira azure-devops sqlalchemy python-dateutil tiktoken plotly pydantic
   ```

4. **Configure API key**
   
   Create a `.env` file:
   ```powershell
   Copy-Item .env.example .env 
   ```
   
   Edit `.env` and add your credentials:
   ```
   GOOGLE_API_KEY=your-actual-api-key-here
   LLM_MODEL=gemini-3-flash-preview
   LLM_TEMPERATURE=0.3
   .
   .
   .
   ```

5. **Test the installation**
   ```powershell
   python test_system.py
   ```

6. **Run the demo**
   ```powershell
   python -m streamlit run app.py
   ```
   
   The app will automatically open at http://localhost:8501

---

## Usage Guide

### Demo with Sample Tickets (Recommended)
1. Select a sample ticket (Bug Fix / Feature / API Change)
2. Enter your API key in the sidebar (if not in .env)
3. Click "Generate Test Cases"
4. Watch agents work in real-time
5. Review generated test cases and QA roadmap
6. Download Excel file

### Using Custom Tickets
1. Switch to "Custom Input" tab
2. Enter your ticket details (ID, title, description, acceptance criteria)
3. Click "Generate Test Cases"
4. Review and download results

### Using Live Integration (Jira/Azure DevOps)

**Jira Setup:**
1. Get API token from https://id.atlassian.com/manage/api-tokens
2. Add to `.env`:
   ```env
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_token_here
   ```
3. In app → "Live Integration" tab → Select Jira → Enter ticket ID (e.g., `PROJ-123`)

**Azure DevOps Setup:**
1. Create Personal Access Token (User Settings → PAT → Work Items Read & Write)
2. Add to `.env`:
   ```env
   AZURE_DEVOPS_ORG=https://dev.azure.com/your-org
   AZURE_DEVOPS_PAT=your_token_here
   AZURE_DEVOPS_PROJECT=YourProject
   ```
3. In app → "Live Integration" tab → Select Azure DevOps → Enter work item ID (e.g., `12345`)

**Sync Results Back:**
- After generating test cases, go to "Export & Sync" tab
- Choose options: post comment, attach Excel, create subtasks
- Click "Sync to Ticket System"

---

## Local Deployment

### Performance Optimization

**Speed up demo:**
```env
# Use Gemini Flash for faster results
LLM_MODEL=gemini-2.0-flash-exp
```

**Warm up the system:**
```powershell
# Run once before demo to cache imports
python -c "from agents import AgentOrchestrator; import streamlit"
```

**Close background apps:**
- Browser tabs
- Heavy applications
- Background updates

---

## Cloud Deployment (Optional)

### Streamlit Cloud (Free Hosting)

1. **Push to GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - Ticket-to-Test AI"
   git branch -M main
   git remote add origin https://github.com/your-username/ticket-to-test-ai.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect your GitHub repo
   - Set main file: `app.py`
   - Add secrets (API keys) in Advanced settings
   - Click "Deploy"

3. **Configure Secrets**
   In Streamlit Cloud dashboard, add:
   ```toml
   GOOGLE_API_KEY = "your-gemini-api-key-here"
   LLM_MODEL = "gemini-3-flash-preview"
   ```

---

## Troubleshooting

### "Module not found"
```powershell
# Verify virtual environment is activated
Get-Command python | Select-Object Source
# Should show path inside venv folder

# Reinstall dependencies
pip install streamlit google-generativeai langchain langgraph python-dotenv openpyxl pandas requests jira azure-devops sqlalchemy python-dateutil tiktoken plotly pydantic --force-reinstall
```
### "Streamlit won't start"
```powershell
# Kill existing Streamlit processes
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"} | Stop-Process

# Restart
python -m streamlit run app.py
```

### "Agents take too long"
- Switch to `gemini-2.0-flash-exp` in .env (faster model)
- Check internet connection speed
- Verify Google AI service status

### "Excel file won't download"
```powershell
# Check outputs directory exists
New-Item -ItemType Directory -Force -Path outputs

# Check permissions
icacls outputs
```

### "Integration connection failed"
- **Jira:** Check URL includes `https://`, verify email and API token
- **Azure DevOps:** Verify org URL format, ensure PAT has Work Items permissions
- **Both:** Test token hasn't expired, regenerate if needed

### "Ticket not found"
- **Jira:** Use full ID format like `PROJ-123` (not just `123`)
- **Azure DevOps:** Use numeric ID only (e.g., `12345`)
- Verify you have permissions to view the ticket

### "Pydantic V1 compatibility warning" (Python 3.14+)
```
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14
```
**This is harmless** - the app will work fine. Some dependencies still use Pydantic V1 internally. To eliminate the warning, use Python 3.12 instead of 3.14.

---

## Demo Day Checklist

### Before Presentation (30 minutes prior)

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list`)
- [ ] `.env` file configured with valid API key
- [ ] Google AI account has API access enabled
- [ ] Run full system test: `python test_system.py`
- [ ] Streamlit app tested and running
- [ ] Sample tickets load correctly
- [ ] Test case generation works (run full test)
- [ ] Excel download works
- [ ] Browser cache cleared
- [ ] Full screen mode ready (F11)
- [ ] Close unnecessary applications
- [ ] Internet connection stable
- [ ] Have backup plan ready (pre-generated results)

### Backup Plan

**In case of API failures:**

1. Pre-generate results before demo:
   ```powershell
   # Save a successful run
   python -m streamlit run app.py
   # Generate and save Excel file
   ```

2. Have ready:
   - Screenshots of each stage
   - Pre-downloaded Excel file
   - Agent workflow diagram

3. Fallback presentation:
   - Show code structure
   - Walk through architecture
   - Display Excel output
   - Explain what should have happened

---

## Production Deployment (Future)

### Next Steps for Real Usage

1. **Jira/Azure DevOps Integration**
   - Implement real API integrations
   - Add webhook support for auto-updates
   - OAuth authentication

2. **Database Layer**
   - Add SQLite/PostgreSQL for versioning
   - Store ticket → test case history
   - Audit trail for compliance

3. **Sync Agent**
   - Post results back to tickets as comments
   - Create test case subtasks
   - Update on ticket changes

4. **Authentication**
   - User management
   - Team-based configurations
   - Role-based access control

5. **Custom Templates**
   - Organization-specific test case formats
   - Custom QA strategies per project type
   - Configurable agent behavior

### Security Considerations

- API key management (use secrets manager)
- Data encryption in transit and at rest
- PII masking for sensitive data
- On-premise deployment option
- SOC 2 compliance roadmap

---

## System Requirements

### Minimum
- Python 3.9+
- 4GB RAM
- Internet connection
- Modern web browser

### Recommended
- Python 3.11+
- 8GB RAM
- Fast internet (for API calls)
- Chrome/Firefox latest version

---

## Cost Estimation

### Development/Demo
- **Gemini Pro:** $0.05 per ticket
- **Gemini Flash:** $0.005 per ticket
- **Demo costs:** Free tier available (60 requests/min)

### Production Scale
- **200 tickets/month:** ~$10/month (Gemini Pro) or ~$1/month (Gemini Flash)
- **1000 tickets/month:** ~$50/month (Gemini Pro) or ~$5/month (Gemini Flash)

**ROI Comparison:**
- Cost: ~$50/month
- Savings: $6,250/sprint (for 5-person QA team)
- **Net benefit: $6,200/sprint**

---

## Support & Resources

### Documentation
- LangGraph: https://langchain-ai.github.io/langgraph/
- Google AI API: https://ai.google.dev/docs
- Streamlit: https://docs.streamlit.io

### Community
- LangChain Discord
- Streamlit Forum
- r/QualityAssurance (Reddit)

### Getting Help
- Check console output for detailed errors
- Review `agent_logs` in the results
- Ensure Python 3.9+ is being used
- Verify API key is valid and has credits
