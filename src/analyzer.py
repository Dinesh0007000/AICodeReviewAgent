import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def analyze_file(self, file_path, lang):
        logger.info(f"Starting analysis for {file_path} with language {lang}")
        if lang == 'python':
            cmd = ['pylint', file_path]
        elif lang == 'javascript':
            cmd = ['eslint', file_path]
        elif lang == 'java':
            cmd = ['java', '-jar', 'checkstyle.jar', '-c', 'sun_checks.xml', file_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Command output: {result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return e.stderr
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return str(e)
