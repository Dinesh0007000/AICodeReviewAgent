import sys
import os
import logging

# Add the src directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import os
from flask import Flask, request
from src.analyzer import CodeAnalyzer  # Adjust import as needed

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    extract_path = "input_codebase"
    os.makedirs(extract_path, exist_ok=True)
    analyzer = CodeAnalyzer()
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
                try:
                    with open(file_path, 'r') as f:
                        logger.info(f"File content of {file_path}:\n{f.read()}")
                    file_issues = analyzer.analyze_file(file_path, lang)
                    logger.info(f"Issues found in {file_path}: {file_issues}")
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {str(e)}")
    return "Analysis complete"  # Adjust as needed
