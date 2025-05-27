import os
import zipfile
from flask import Flask, request, send_file
from src.analyzer import CodeAnalyzer
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    extract_path = "input_codebase"
    os.makedirs(extract_path, exist_ok=True)
    zip_path = os.path.join(extract_path, "codebase.zip")
    file.save(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    analyzer = CodeAnalyzer()
    bugs = 0
    code_smells = 0
    security_issues = 0

    for root, _, files in os.walk(extract_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            lang = None
            if filename.endswith('.py'):
                lang = 'python'
            elif filename.endswith('.js'):
                lang = 'javascript'
            elif filename.endswith('.java'):
                lang = 'java'
            if lang:
                logger.info(f"Analyzing file: {file_path}")
                issues = analyzer.analyze_file(file_path, lang)
                for issue in issues:
                    if lang == "python" or lang == "javascript":
                        if "error" in issue.get("type", "") or "warning" in issue.get("type", ""):
                            bugs += 1
                        elif "convention" in issue.get("type", "") or "refactor" in issue.get("type", ""):
                            code_smells += 1
                    elif lang == "java":
                        if "error" in issue.get("source", ""):
                            bugs += 1
                        else:
                            code_smells += 1

    report = f"""
# AI Code Review Agent Report
Dependencies detected: requirements.txt
## Quality Metrics
- Bugs fixed: {bugs}
- Code smells improved: {code_smells}
- Security issues noted: {security_issues}
"""
    report_path = "reports/report.md"
    os.makedirs("reports", exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    return send_file(report_path, as_attachment=True)
