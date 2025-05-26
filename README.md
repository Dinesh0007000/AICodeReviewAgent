AI Code Review Agent
A tool to analyze and improve codebases, supporting Python, JavaScript, and Java. Meets the requirements of the provided FRD for an internship project.
Setup

Clone Repository:
git clone <your-repo-url>
cd ai_code_review_agent


Python Environment:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt


Node.js Dependencies:
npm install


Java Tools:

Download checkstyle-10.17.0-all.jar and spotbugs-4.8.6.jar to tools/.
Install google-java-format (e.g., brew install google-java-format).


Sample Codebase:

Place a test codebase in input_codebase/ or use a ZIP/Git URL.



Usage
Command-Line Interface
python src/main.py input_codebase --output output_codebase --config config.json

Web Interface
python src/app.py


Open http://localhost:5000 to upload a ZIP file and configure settings.

API
curl -X POST -H "Content-Type: application/json" -d '{"input_path": "input_codebase", "config": {}}' http://localhost:5000/api/analyze

Deployment

Install Vercel CLI: npm install -g vercel.
Run vercel and follow prompts.
Push to GitHub for CI/CD integration.

Features

Supports Python, JavaScript, Java (FR-1.2).
Analyzes syntax, bugs, security, and code smells (FR-2.1 to FR-2.6).
Improves code with formatting and documentation (FR-3.1 to FR-3.6).
Generates reports with diffs and metrics (FR-4.1 to FR-4.6).
Configurable via CLI, web, or API (FR-5.1 to FR-5.4, IR-2.1).

Limitations

Performance optimization (FR-2.6, FR-3.2) is a placeholder.
Advanced refactoring for JavaScript/Java is limited to formatting and comments.

Testing

Create a test codebase in tests/ with sample .py, .js, .java files.
Run CLI and web app to verify reports and improvements.

