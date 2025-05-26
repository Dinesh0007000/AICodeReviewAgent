import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, render_template, send_file, jsonify
import zipfile
import shutil
import json
import tempfile
from analyzer import CodeAnalyzer
from improver import CodeImprover
from output_generator import OutputGenerator
from config import Config

app = Flask(__name__)
# Use /tmp/ for Vercel serverless environment
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("codebase")
        config_data = {
            "priorities": {
                "security": int(request.form.get("security_priority", 1)),
                "performance": int(request.form.get("performance_priority", 1)),
                "readability": int(request.form.get("readability_priority", 1))
            },
            "style": {
                "python": {"line_length": int(request.form.get("line_length_python", 88))},
                "javascript": {"printWidth": int(request.form.get("line_length_js", 80))},
                "java": {"maxLineLength": int(request.form.get("line_length_java", 100))}
            },
            "exclude": request.form.get("exclude", "").split(","),
            "aggressiveness": request.form.get("aggressiveness", "moderate")
        }
        
        config_path = os.path.join(UPLOAD_FOLDER, "temp_config.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        config = Config(config_path)
        
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)
        extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
        if input_path.endswith(".zip"):
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
            input_path = extract_path
        
        output_dir = os.path.join(UPLOAD_FOLDER, "output")
        analyzer = CodeAnalyzer(config)
        improver = CodeImprover(config)
        output_gen = OutputGenerator(config, output_dir)
        
        supported_extensions = {".py": "python", ".js": "javascript", ".java": "java"}
        code_files = []
        dependencies = []
        for root, _, files in os.walk(input_path):
            if any(exclude in root for exclude in config.get("exclude")):
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in supported_extensions:
                    code_files.append((os.path.join(root, f), supported_extensions[ext]))
                elif f in ('requirements.txt', 'package.json', 'pom.xml'):
                    dependencies.append(os.path.join(root, f))
        
        for file_path, lang in code_files:
            analysis_results = analyzer.analyze_file(file_path, lang)
            improved_code = improver.improve_code(file_path, analysis_results, lang)
            output_gen.save_improved_code(file_path, improved_code, analysis_results)
        
        report_path = output_gen.generate_report(dependencies)
        
        # Clean up
        shutil.rmtree(extract_path, ignore_errors=True)
        os.remove(config_path)
        os.remove(input_path)
        
        return send_file(report_path, as_attachment=True)
    
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    # REST API for programmatic interaction (IR-2.1)
    data = request.get_json()
    input_path = data.get("input_path")
    config_data = data.get("config", {})
    
    config_path = os.path.join(UPLOAD_FOLDER, "temp_config.json")
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    config = Config(config_path)
    
    output_dir = os.path.join(UPLOAD_FOLDER, "output")
    analyzer = CodeAnalyzer(config)
    improver = CodeImprover(config)
    output_gen = OutputGenerator(config, output_dir)
    
    supported_extensions = {".py": "python", ".js": "javascript", ".java": "java"}
    code_files = []
    dependencies = []
    for root, _, files in os.walk(input_path):
        if any(exclude in root for exclude in config.get("exclude")):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_extensions:
                code_files.append((os.path.join(root, f), supported_extensions[ext]))
            elif f in ('requirements.txt', 'package.json', 'pom.xml'):
                dependencies.append(os.path.join(root, f))
    
    for file_path, lang in code_files:
        analysis_results = analyzer.analyze_file(file_path, lang)
        improved_code = improver.improve_code(file_path, analysis_results, lang)
        output_gen.save_improved_code(file_path, improved_code, analysis_results)
    
    report_path = output_gen.generate_report(dependencies)
    
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    shutil.rmtree(output_dir, ignore_errors=True)
    os.remove(config_path)
    
    return jsonify({"report": report_content, "output_dir": output_dir})

if __name__ == "__main__":
    app.run(debug=True)
