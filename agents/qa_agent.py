from prompts.qa_prompt import (
    FUNCTIONAL_TEST_PROMPT,
    API_TEST_PROMPT,
    SECURITY_TEST_PROMPT,
)

from services.gemini_service import ask_gemini
from services.groq_service import ask_groq 

class QAAgent:

    def get_response(self, prompt, provider):
        """
        Helper method jo selected provider ke basis par sahi service call karega.
        """
        if provider == "Groq (Llama 3.3)":
            return ask_groq(prompt)
        else:
            return ask_gemini(prompt)

    def _get_enterprise_suffix(self):
        return """
\n\n
---
### 💼 ENTERPRISE QA COMPLIANCE ADDENDUM (ISTQB & AUTOMATION MANDATE)
As a Senior QA Lead, append the following elite matrices strictly to the output structure:
1. Ensure the main test case table includes explicit columns for: [Test ID | Priority (P0/P1/P2) | Severity (Blocker/Critical/Normal) | Scenario Description | Expected Validation].
2. Provide a dedicated section for "⚙️ Automation-Ready Script Specifications" containing actionable BDD Gherkin syntax (Given-When-Then) blocks for core execution flows.
3. Provide a section for "⚠️ Heuristic Bug Predictions & Boundary Flaws" detailing potential technical edge-case bugs, race conditions, or unhandled logical states based on the requirements.
Do not embed complex HTML elements or literal line breaks inside the Markdown table cells to keep the system report pipeline safe.
"""

    def generate_functional_tests(self, requirement, provider="Gemini 2.5 Flash"):
        # Original prompt + Heavy Enterprise Parameters
        prompt = f"""
{FUNCTIONAL_TEST_PROMPT}

Requirement Context:
{requirement}

{self._get_enterprise_suffix()}
"""
        return self.get_response(prompt, provider)

    def generate_api_tests(self, requirement, provider="Gemini 2.5 Flash"):
        prompt = f"""
{API_TEST_PROMPT}

Requirement Context:
{requirement}

\n\n
---
### 🔌 ENTERPRISE API TEST COMPLIANCE
Ensure the API test suite is structurally formatted into a clear Markdown Table with explicit columns for: [Test ID | Method & Endpoint | Payload/Params | Expected Status | Response Body Verification | Priority].
Also append a section titled "🚧 Advanced Security & Performance Resiliency Cases" (Idempotency tokens, data truncation limits, missing authentication headers).
"""
        return self.get_response(prompt, provider)

    def generate_security_tests(self, requirement, provider="Gemini 2.5 Flash"):
        prompt = f"""
{SECURITY_TEST_PROMPT}

Requirement Context:
{requirement}

\n\n
---
### 🔒 ENTERPRISE SECURITY PENETRATION MANDATE
Structure your analysis to output a professional vulnerability assessment matrix mapping directly to OWASP Top 10 vulnerabilities. 
Include a clean Markdown table with columns: [Vulnerability ID | OWASP Category | Attack Vector/Payload Input | Expected Secure Behavior | Severity].
"""
        return self.get_response(prompt, provider)

    def generate_bug_report(self, bug_description, provider="Gemini 2.5 Flash"):
        """
        Experienced Senior QA Defect Analysis Engine: Takes a raw bug symptom or observation 
        from any website/app and structures it into an elite Jira-ready Bug Report.
        """
        prompt = f"""
You are a Principal QA Engineer. Analyze the following raw bug description/symptom found in the system and convert it into a highly professional, enterprise-grade Defect/Bug Report ready for senior developers.

Raw Bug Input:
\"\"\"
{bug_description}
\"\"\"

Format your output exactly into these structured sections:
1. ##  Defect Executive Summary (Clear title, Severity, Priority: P0/P1/P2, and Component impacted)
2. ##  Steps to Reproduce (Highly technical, sequential, isolated replication steps)
3. ##  Actual vs Expected Behavior Matrix (Clear juxtaposition of the failure state vs target architecture)
4. ##  Probable Root Cause & Developer Fix Suggestions (Heuristic assessment of why the code broke, e.g., missing null checks, race conditions, unhandled asynchronous state)
"""
        return self.get_response(prompt, provider)