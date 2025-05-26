import black
import ast
import astunparse
import subprocess
import os

class CodeImprover:
    def __init__(self, config):
        self.config = config
    
    def improve_code(self, file_path, analysis_results, language):
        with open(file_path, 'r') as f:
            code = f.read()
        
        improved_code = code
        aggressiveness = self.config.get("aggressiveness")
        
        if language == "python":
            # Format with black (FR-3.4)
            try:
                improved_code = black.format_str(code, mode=black.FileMode(line_length=self.config.get_style("python")["line_length"]))
            except Exception:
                pass
            
            # Refactor: Add docstrings (FR-3.1, FR-3.5)
            if aggressiveness != "low":
                try:
                    tree = ast.parse(improved_code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if not any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Str) for n in node.body):
                                node.body.insert(0, ast.Expr(value=ast.Str(s=f"Function {node.name} description")))
                    improved_code = astunparse.unparse(tree)
                except Exception:
                    pass
            
            # Security fixes placeholder (FR-3.3)
            for issue in analysis_results["security_issues"]:
                improved_code = f"# TODO: Address security issue: {issue}\n{improved_code}"
        
        elif language == "javascript":
            # Format with Prettier (FR-3.4)
            prettier_cmd = f"npx prettier --write {file_path} --print-width {self.config.get_style('javascript')['printWidth']}"
            subprocess.run(prettier_cmd, shell=True, capture_output=True)
            with open(file_path, 'r') as f:
                improved_code = f.read()
            
            # Add JSDoc (FR-3.5)
            if aggressiveness != "low":
                improved_code = f"/** @description Improved by AI Code Review Agent */\n{improved_code}"
            
            # Security fixes placeholder (FR-3.3)
            for issue in analysis_results["security_issues"]:
                improved_code = f"// TODO: Address security issue: {issue}\n{improved_code}"
        
        elif language == "java":
            # Format with google-java-format (FR-3.4)
            google_java_format_cmd = f"google-java-format --replace {file_path}"
            subprocess.run(google_java_format_cmd, shell=True, capture_output=True)
            with open(file_path, 'r') as f:
                improved_code = f.read()
            
            # Add JavaDoc (FR-3.5)
            if aggressiveness != "low":
                improved_code = f"/** Improved by AI Code Review Agent */\n{improved_code}"
            
            # Security fixes placeholder (FR-3.3)
            for issue in analysis_results["security_issues"]:
                improved_code = f"// TODO: Address security issue: {issue}\n{improved_code}"
        
        # Performance and resource optimization placeholder (FR-3.2, FR-3.6)
        improved_code = f"// TODO: Optimize performance and resources\n{improved_code}"
        
        return improved_code