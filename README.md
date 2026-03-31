# AppGuard

AppGuard is an AI-powered legal support prototype designed to assist workers in vulnerable situations, specifically focusing on moral and sexual harassment in the workplace.

The project leverages Artificial Intelligence to humanize the initial reporting process, helping victims understand their situation and instructing them on their rights based on the Brazilian Labor Law (CLT) and the Penal Code.

**Note:** This is an academic study prototype. The tool acts as an informational \"co-pilot\" and does not replace professional legal advice from a qualified lawyer.

## Key Features
- **Empathetic Intake:** Processes free-text reports using Large Language Models (LLMs) to provide supportive and non-judgmental initial feedback.
- **Legal Classification:** Analyzes reports to identify potential legal violations based on labor regulations and criminal statutes.
- **Rights Guidance:** Instructs users on the next steps to take and what kind of evidence (emails, messages, witnesses) is necessary for a legal case.
- **Report Structuring:** Generates a technical \"skeleton\" or summary of the events to facilitate the work of lawyers or public labor prosecutors (MPT).

## Project Structure
- `app.py`: Main user interface built with Streamlit.
- `core/engine.py`: The \"brain\" of the app, handling LLM integration and processing logic.
- `core/prompts.py`: Modular Prompt Engineering system tailored for legal terminology and victim support.
- `assets/custom.css`: Custom CSS for a clean, professional, and accessible UI.  <!-- Adjusted path based on tabs -->

## Tech Stack
- **Language:** Python
- **Web Framework:** Streamlit
- **AI/LLM:** Integration with state-of-the-art models (DeepSeek / Gemma / OpenAI)
- **Methodology:** Advanced Prompt Engineering for legal contexts

## Quick Start
### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the application:
```bash
streamlit run app.py
```

