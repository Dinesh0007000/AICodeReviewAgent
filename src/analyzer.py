import subprocess
import json
import xml.etree.ElementTree as ET
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def __init__(self):
        self.checkstyle_jar = "/vercel/path0/checkstyle.jar"
        self.sun_checks_xml = "/vercel/path0/sun_checks.xml"
        self.eslint_config = "/vercel/path0/.eslintrc.json"

    def analyze_file(self, file_path, lang):
        logger.info(f"Starting analysis for {file_path} with language {lang}")
        if lang == "python":
            try:
                result = subprocess.run(
                    ["pylint", "--output-format=json", file_path],
                    capture_output=True, text=True
                )
                logger.info(f"Pylint result: {result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except Exception as e:
                logger.error(f"Pylint error: {str(e)}")
                return []

        elif lang == "javascript":
            try:
                result = subprocess.run(
                    ["eslint", "--format", "json", "--config", self.eslint_config, file_path],
                    capture_output=True, text=True
                )
                logger.info(f"ESLint result: {result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except Exception as e:
                logger.error(f"ESLint error: {str(e)}")
                return []

        elif lang == "java":
            try:
                result = subprocess.run(
                    ["java", "-jar", self.checkstyle_jar, "-c", self.sun_checks_xml, "-f", "xml", file_path],
                    capture_output=True, text=True
                )
                logger.info(f"Checkstyle result: {result.stdout}")
                root = ET.fromstring(result.stdout)
                issues = []
                for file in root.findall("file"):
                    for error in file.findall("error"):
                        issues.append({
                            "line": error.get("line"),
                            "message": error.get("message"),
                            "source": error.get("source")
                        })
                return issues
            except Exception as e:
                logger.error(f"Checkstyle error: {str(e)}")
                return []

        return []
