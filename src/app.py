import sys
import os
import logging

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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return f"Internal Server Error: {str(e)}", 500

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        logger.info("Received POST request to /")
        file = request.files.get("codebase")
        if not file or not file.filename:
            logger.error("No file uploaded or invalid file")
            return "No file uploaded or invalid file", 400

        logger.info("Creating config data")
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
        
        config_path = None
        input_path = None
        extract_path = None
        report_path = None
        
        try:
            logger.info(f"Writing config to {UPLOAD_FOLDER}/temp_config.json")
            config_path = os.path.join(UPLOAD_FOLDER, "temp_config.json")
            with open(config_path, "w") as f:
                json.dump(config_data, f)
            logger.info("Initializing Config class")
            config = Config(config_path)
        except Exception as e:
            logger.error(f"Failed to create config: {str(e)}", exc_info=True)
            return f"Failed to create config: {str(e)}", 500
        
        try:
            logger.info(f"Saving uploaded file to {UPLOAD_FOLDER}/{file.filename}")
            input_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(input_path)
            extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
            if input_path.endswith(".zip"):
                logger.info(f"Extracting ZIP to {extract_path}")
                with zipfile.ZipFile(input_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                input_path = extract_path
            else:
                extract_path = None  # No extraction if not a ZIP
        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file")
            return "Invalid ZIP file", 400
        except Exception as e:
            logger.error(f"Failed to extract ZIP file: {str(e)}", exc_info=True)
            return f"Failed to extract ZIP file: {str(e)}", 500
        
        try:
            logger.info(f"Creating output directory at {UPLOAD_FOLDER}/output")
            output_dir = os.path.join(UPLOAD_FOLDER, "output")
            os.makedirs(output_dir, exist_ok=True)
            logger.info("Initializing CodeAnalyzer")
            analyzer = CodeAnalyzer(config)
            logger.info("Initializing CodeImprover")
            improver = CodeImprover(config)
            logger.info("Initializing OutputGenerator")
            output_gen = OutputGenerator(config, output_dir)
        except Exception as e:
            logger.error(f"Failed to initialize analyzer/improver: {str(e)}", exc_info=True)
            return f"Failed to initialize analyzer/improver: {str(e)}", 500
        
        supported_extensions = {".py": "python", ".js": "javascript", ".java": "java"}
        code_files = []
        dependencies = []
        try:
            logger.info(f"Scanning directory {input_path}")
            for root, _, files in os.walk(input_path):
                if any(exclude in root for exclude in config.get("exclude")):
                    continue
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in supported_extensions:
                        code_files.append((os.path.join(root, f), supported_extensions[ext]))
                    elif f in ('requirements.txt', 'package.json', 'pom.xml'):
                        dependencies.append(os.path.join(root, f))
        except Exception as e:
            logger.error(f"Failed to scan directory: {str(e)}", exc_info=True)
            return f"Failed to scan directory: {str(e)}", 500
        
        logger.info(f"Found {len(code_files)} code files to process")
        for file_path, lang in code_files:
            try:
                logger.info(f"Analyzing file {file_path} ({lang})")
                analysis_results = analyzer.analyze_file(file_path, lang)
                logger.info(f"Improving code for {file_path}")
                improved_code = improver.improve_code(file_path, analysis_results, lang)
                logger.info(f"Saving improved code for {file_path}")
                output_gen.save_improved_code(file_path, improved_code, analysis_results)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {str(e)}", exc_info=True)
                return f"Failed to process file {file_path}: {str(e)}", 500
        
        try:
            logger.info("Generating report")
            report_path = output_gen.generate_report(dependencies)
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}", exc_info=True)
            return f"Failed to generate report: {str(e)}", 500
        
        # Send the report before cleanup
        logger.info(f"Sending report file: {report_path}")
        response = send_file(report_path, as_attachment=True)
        
        # Clean up after sending the response
        logger.info(f"Cleaning up: removing {extract_path}, {config_path}, {input_path}")
        if extract_path and os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        if config_path and os.path.exists(config_path):
            os.remove(config_path)
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
        
        return response

    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    logger.info("Received POST request to /api/analyze")
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

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content, suppresses the 404 error

if __name__ == "__main__":
    app.run(debug=True)
