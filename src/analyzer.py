import subprocess
import json
import xml.etree.ElementTree as ET

class CodeAnalyzer:
    def __init__(self, config):
        self.config = config

    def analyze_file(self, file_path, lang):
        if lang == "python":
            try:
                result = subprocess.run(
                    ["pylint", file_path, "--output-format=json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return json.loads(result.stdout)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Pylint failed: {e.stderr}")
            except FileNotFoundError:
                raise Exception("Pylint not found. Ensure it is installed in the environment.")

        elif lang == "javascript":
            try:
                result = subprocess.run(
                    ["npx", "eslint", file_path, "--format", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return json.loads(result.stdout)
            except subprocess.CalledProcessError as e:
                raise Exception(f"ESLint failed: {e.stderr}")
            except FileNotFoundError:
                raise Exception("ESLint not found. Ensure it is installed in the environment.")

        elif lang == "java":
            try:
                result = subprocess.run(
                    ["java", "-jar", "checkstyle.jar", "-c", "sun_checks.xml", "-f", "xml", file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Parse Checkstyle XML output
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
            except subprocess.CalledProcessError as e:
                raise Exception(f"Checkstyle failed: {e.stderr}")
            except FileNotFoundError:
                raise Exception("Checkstyle or Java not found. Ensure they are installed in the environment.")

        else:
            raise ValueError(f"Unsupported language: {lang}")
