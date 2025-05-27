import subprocess
import json
import xml.etree.ElementTree as ET
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def __init__(self, config):
        self.config = config

    def analyze_file(self, file_path, lang):
        logger.info(f"Starting analysis for {file_path} with language {lang}")

        if lang == "python":
            try:
                logger.info("Running Pylint...")
                result = subprocess.run(
                    ["pylint", file_path, "--output-format=json"],
                    capture_output=True,
                    text=True
                )
                logger.info(f"Pylint command executed with return code: {result.returncode}")
                logger.info(f"Pylint stdout: {result.stdout}")
                logger.info(f"Pylint stderr: {result.stderr}")
                if result.returncode & 32:  # Exit code 32 means fatal error (e.g., file not found)
                    raise Exception(f"Pylint failed with fatal error: {result.stderr}\n{result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except FileNotFoundError as e:
                logger.error(f"Pylint not found: {str(e)}")
                raise Exception("Pylint not found. Ensure it is installed in the environment.")
            except json.JSONDecodeError as e:
                logger.error(f"Pylint output is not valid JSON: {result.stdout}")
                raise Exception(f"Pylint output is not valid JSON: {result.stdout}")

        elif lang == "javascript":
            try:
                logger.info("Running ESLint...")
                result = subprocess.run(
                    ["npx", "eslint", file_path, "--format", "json"],
                    capture_output=True,
                    text=True
                )
                logger.info(f"ESLint command executed with return code: {result.returncode}")
                logger.info(f"ESLint stdout: {result.stdout}")
                logger.info(f"ESLint stderr: {result.stderr}")
                if result.returncode not in [0, 1]:  # 1 means issues found, which is fine
                    raise Exception(f"ESLint failed: {result.stderr}\n{result.stdout}")
                return json.loads(result.stdout) if result.stdout else []
            except FileNotFoundError as e:
                logger.error(f"ESLint not found: {str(e)}")
                raise Exception("ESLint not found. Ensure it is installed in the environment.")
            except json.JSONDecodeError as e:
                logger.error(f"ESLint output is not valid JSON: {result.stdout}")
                raise Exception(f"ESLint output is not valid JSON: {result.stdout}")

        elif lang == "java":
            try:
                # Look for checkstyle.jar and sun_checks.xml in the parent directory (project root)
                checkstyle_jar = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkstyle.jar")
                sun_checks_xml = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sun_checks.xml")
                logger.info(f"Running Checkstyle with JAR: {checkstyle_jar} and config: {sun_checks_xml}")
                result = subprocess.run(
                    ["java", "-jar", checkstyle_jar, "-c", sun_checks_xml, "-f", "xml", file_path],
                    capture_output=True,
                    text=True
                )
                logger.info(f"Checkstyle command executed with return code: {result.returncode}")
                logger.info(f"Checkstyle stdout: {result.stdout}")
                logger.info(f"Checkstyle stderr: {result.stderr}")
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
            except FileNotFoundError as e:
                logger.error(f"Checkstyle or Java not found: {str(e)}")
                raise Exception("Checkstyle or Java not found. Ensure they are installed in the environment.")
            except ET.ParseError as e:
                logger.error(f"Checkstyle output is not valid XML: {result.stdout}")
                raise Exception(
                    f"Checkstyle failed: {result.stderr}\nCheckstyle output is not valid XML: {result.stdout}"
                )

        else:
            raise ValueError(f"Unsupported language: {lang}")
