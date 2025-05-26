import pylint.lint
import bandit
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import ast
import os
import subprocess
import json

class CodeAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def analyze_file(self, file_path, language):
        results = {
            "syntax_errors": [],
            "bugs": [],
            "security_issues": [],
            "code_smells": [],
            "complexity_metrics": {},
            "performance_issues": []
        }
        
        # Weight results based on priorities (FR-5.1)
        priorities = self.config.get("priorities")
        
        if language == "python":
            # Syntax and bug analysis (FR-2.1)
            try:
                with open(file_path, 'r') as f:
                    tree = ast.parse(f.read())
            except SyntaxError as e:
                results["syntax_errors"].append(str(e))
                return results
            
            # Pylint for bugs and code smells (FR-2.1, FR-2.4)
            pylint_output = []
            pylint.lint.Run([file_path, "--output-format=json"], reporter=pylint.lint.MessageReporter(pylint_output))
            for msg in pylint_output:
                if msg["type"] in ["error", "fatal"]:
                    results["bugs"].append(msg["message"])
                elif msg["type"] in ["convention", "refactor"]:
                    results["code_smells"].append(msg["message"])
            
            # Bandit for security issues (FR-2.2)
            if priorities["security"] > 0:
                bandit_cmd = f"bandit -r {file_path} -f json"
                bandit_output = subprocess.getoutput(bandit_cmd)
                try:
                    bandit_results = json.loads(bandit_output)
                    for issue in bandit_results.get("results", []):
                        results["security_issues"].append(issue["issue_text"])
                except json.JSONDecodeError:
                    results["security_issues"].append("Bandit analysis failed")
            
            # Complexity and maintainability (FR-2.5)
            with open(file_path, 'r') as f:
                code = f.read()
            results["complexity_metrics"]["cyclomatic"] = cc_visit(code)
            results["complexity_metrics"]["maintainability"] = mi_visit(code, multi=True)
        
        elif language == "javascript":
            # ESLint for syntax, bugs, code smells (FR-2.1, FR-2.4)
            eslint_cmd = f"npx eslint {file_path} --format json"
            eslint_output = subprocess.getoutput(eslint_cmd)
            try:
                eslint_results = json.loads(eslint_output)
                for file in eslint_results:
                    for msg in file.get("messages", []):
                        if msg["severity"] == 2:
                            results["bugs"].append(msg["message"])
                        elif msg["severity"] == 1:
                            results["code_smells"].append(msg["message"])
            except json.JSONDecodeError:
                results["bugs"].append("ESLint analysis failed")
            
            # npm audit for security (FR-2.2)
            if priorities["security"] > 0:
                npm_audit_cmd = f"npm audit --json"
                npm_audit_output = subprocess.getoutput(npm_audit_cmd)
                try:
                    audit_results = json.loads(npm_audit_output)
                    for issue in audit_results.get("vulnerabilities", {}).values():
                        results["security_issues"].append(issue["title"])
                except json.JSONDecodeError:
                    results["security_issues"].append("npm audit failed")
            
            # Complexity (FR-2.5)
            results["complexity_metrics"]["note"] = "Use jscpd or similar for JS complexity"
        
        elif language == "java":
            # Checkstyle for style and code smells (FR-2.4)
            checkstyle_cmd = f"java -jar tools/checkstyle-10.17.0-all.jar -c /sun_checks.xml {file_path}"
            checkstyle_output = subprocess.getoutput(checkstyle_cmd)
            results["code_smells"].extend(checkstyle_output.splitlines())
            
            # SpotBugs for bugs and security (FR-2.1, FR-2.2)
            if priorities["security"] > 0:
                spotbugs_cmd = f"java -jar tools/spotbugs-4.8.6.jar -textui {file_path}"
                spotbugs_output = subprocess.getoutput(spotbugs_cmd)
                results["bugs"].extend(spotbugs_output.splitlines())
            
            # Complexity (FR-2.5)
            results["complexity_metrics"]["note"] = "Use PMD or CKJM for Java complexity"
        
        # Performance analysis placeholder (FR-2.6)
        if priorities["performance"] > 0:
            results["performance_issues"].append(f"Performance analysis TBD for {language}")
        
        return results