import os
import shutil
import tempfile
import zipfile  # Moved to top
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from analyzer import CodeAnalyzer
from improver import CodeImprover
from output_generator import OutputGenerator

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('codebase')
        if not file:
            return "No file uploaded", 400

        filename = secure_filename(file.filename)
        zip_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(zip_path)

        config = {
            "priorities": {
                "security": int(request.form.get('security_priority', 1)),
                "performance": int(request.form.get('performance_priority', 1)),
                "readability": int(request.form.get('readability_priority', 1))
            },
            "style_prefs": {
                "line_length_python": int(request.form.get('line_length_python', 88)),
                "line_length_js": int(request.form.get('line_length_js', 80)),
                "line_length_java": int(request.form.get('line_length_java', 100))
            },
            "exclude": request.form.get('exclude', '').split(','),
            "aggressiveness": request.form.get('aggressiveness', 'moderate')
        }

        input_path = os.path.join(UPLOAD_FOLDER, "extracted")
        os.makedirs(input_path, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(input_path)
        except zipfile.BadZipFile:
            return "Invalid ZIP file", 400

        supported_extensions = {".py": "python", ".js": "javascript", ".java": "java"}
        code_files = []
        dependencies = []
        try:
            for root, _, files in os.walk(input_path):
                if any(exclude in root for exclude in config.get("exclude", [])):
                    continue
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in supported_extensions:
                        code_files.append((os.path.join(root, f), supported_extensions[ext]))
                    elif f in ('requirements.txt', 'package.json', 'pom.xml'):
                        dependencies.append(os.path.join(root, f))
        except Exception as e:
            return f"Failed to scan directory: {str(e)}", 500

        analyzer = CodeAnalyzer(config)
        improver = CodeImprover(config)
        output_gen = OutputGenerator(config, "output_codebase")

        analysis_results = {}
        for file_path, lang in code_files:
            try:
                analysis_results[file_path] = analyzer.analyze_file(file_path, lang)
                improved_code = improver.improve_code(file_path, analysis_results[file_path], lang)
                output_gen.save_improved_code(file_path, improved_code, analysis_results[file_path])
            except Exception as e:
                return f"Failed to process file {file_path}: {str(e)}", 500

        try:
            report_path = output_gen.generate_report(dependencies)
        except Exception as e:
            return f"Report generation failed: {str(e)}", 500

        try:
            os.remove(zip_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(input_path)
        except FileNotFoundError:
            pass

        return send_file(report_path, as_attachment=True)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
