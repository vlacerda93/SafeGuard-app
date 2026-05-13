# 🛡️ SafeGuard

SafeGuard is an AI-powered legal support platform designed to assist workers in vulnerable situations, specifically focusing on moral and sexual harassment in the workplace.

The project leverages Artificial Intelligence to humanize the initial reporting process, helping victims understand their situation and instructing them on their rights based on the Brazilian Labor Law (CLT) and the Penal Code.

**Note:** This is an academic study prototype. The tool acts as an informational "co-pilot" and does not replace professional legal advice from a qualified lawyer.

## ✨ Key Features & Recent Updates
- **Empathetic Intake:** Processes free-text reports using Large Language Models (LLMs) to provide supportive and non-judgmental initial feedback.
- **Legal Classification:** Analyzes reports to identify potential legal violations based on labor regulations and criminal statutes, providing qualitative probability assessments.
- **Double Anonymization:** Protects user privacy by automatically scrubbing personal data (names, CPF, company names, etc.) using a dual-layer approach (Regex + LLM) before the text is analyzed.
- **Resilient AI Engine:** Implements a multi-model fallback mechanism (Llama 3.3, Mixtral, etc.) via Groq API to ensure the service remains highly available.
- **Report Structuring:** Generates a technical "skeleton" or summary of the events to facilitate the work of lawyers or public labor prosecutors (MPT).
- **Document Export:** Automatically formats the legal summary into a professional PDF and TXT file for easy download.
- **Panic Button:** Quick exit and session clearing feature for maximum safety.

## 📂 Project Structure
- `safeguardapp/safeguardapp.py`: Main user interface, entirely rebuilt with **Reflex** for a modern, glassmorphism-inspired dark mode design.
- `core/engine.py`: The "brain" of the app, handling multi-LLM integration, data anonymization, and input validation.
- `core/prompts.py`: Modular Prompt Engineering system tailored for legal terminology, strictly avoiding clinical language and exact percentages.
- `core/pdf_generator.py`: Generates professional PDFs using `reportlab` (with `fpdf2` fallback) supporting UTF-8.

## 🛠️ Tech Stack
- **Language:** Python
- **Web Framework:** Reflex (Frontend & Backend)
- **AI/LLM:** Groq API (Llama 3.3 70b, Mixtral)
- **PDF Generation:** ReportLab, FPDF2

## 🚀 Quick Start
### Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the application locally:
```bash
reflex run
```
The app will be available at `http://localhost:3000`.

### Deploying to Reflex Cloud:
```bash
reflex deploy
```
