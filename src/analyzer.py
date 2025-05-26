import subprocess
import json
import xml.etree.ElementTree as ET
import os

class CodeAnalyzer:
    def __init__(self, config):
        self.config = config

    def analyze_file(self, file_path, lang):
        if lang == "python":
            try:
                result = subprocess.run(
                    ["pylint", file_path, "--output-format=json"],
                    capture_output=True,
                    text=True
                )
                if result.returncode & 32:  # Exit code 32 means fatal error (e.g., file not found)
                    raise Exception(f"Pylint failed with fatal error: {result.stderr}\n{result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except FileNotFoundError:
                raise Exception("Pylint not found. Ensure it is installed in the environment.")
            except json.JSONDecodeError:
                raise Exception(f"Pylint output is not valid JSON: {result.stdout}")

        elif lang == "javascript":
            try:
                result = subprocess.run(
                    ["npx", "eslint", file_path, "--format", "json"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0 and result.returncode != 1:  # 1 means issues found, which is fine
                    raise Exception(f"ESLint failed: {result.stderr}\n{result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except FileNotFoundError:
                raise Exception("ESLint not found. Ensure it is installed in the environment.")
            except json.JSONDecodeError:
                raise Exception(f"ESLint output is not valid JSON: {result.stdout}")

        elif lang == "java":
            try:
                # Look for checkstyle.jar and sun_checks.xml in the parent directory (project root)
                checkstyle_jar = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkstyle.jar")
                sun_checks_xml = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sun_checks.xml")
                result = subprocess.run(
                    ["java", "-jar", checkstyle_jar, "-c", sun_checks_xml, "-f", "xml", file_path],
                    capture_output=True,
                    text=True
                )
                # Parse Checkstyle XML output regardless of exit status
                root = ET.fromstring(result.stdout)
                issues = []
                for file in root.findall("file"):
                    for error in file.findall("error"):
                        issues.append({
                            "line": error.get("line"),
                            "column": error.get("column"),
                            "severity": error.get("severity"),
                            "message": error.get("message"),
                            "source": error.get("source")
                        })
                return {"issues": issues}
            except FileNotFoundError:
                raise Exception("Checkstyle or Java not found. Ensure they are installed in the environment.")
            except ET.ParseError:
                raise Exception(f"Checkstyle failed: {result.stderr}\nCheckstyle output is not valid XML: {result.stdout}")

        else:
            raise ValueError(f"Unsupported language: {lang}")
