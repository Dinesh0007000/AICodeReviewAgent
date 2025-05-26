import os
import shutil
import datetime
from pathlib import Path
import difflib
import tempfile

class OutputGenerator:
    def __init__(self, config, output_dir):
        self.config = config
        # Use /tmp/ for Vercel serverless environment
        self.output_dir = os.path.join(tempfile.gettempdir(), output_dir.lstrip("/"))
        self.reports_dir = os.path.join(tempfile.gettempdir(), "reports")
        self.reports = []
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)  # Fixed: Use self.reports_dir instead of "reports"
    
    def save_improved_code(self, file_path, improved_code, analysis_results):
        relative_path = os.path.relpath(file_path, start=os.path.dirname(os.path.dirname(file_path)))
        output_path = os.path.join(self.output_dir, relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(improved_code)
        
        original_code = Path(file_path).read_text()
        diff = list(difflib.unified_diff(
            original_code.splitlines(), improved_code.splitlines(),
            fromfile="original", tofile="improved", lineterm=""
        ))
        self.reports.append({
            "file": file_path,
            "analysis": analysis_results,
            "before": original_code,
            "after": improved_code,
            "diff": diff
        })
    
    def generate_report(self, dependencies):
        report_content = "# AI Code Review Agent Report\n\n"
        report_content += f"Generated on: {datetime.datetime.now()}\n\n"
        
        report_content += "## Project Structure\n"
        report_content += f"Dependencies detected:\n"
        for dep in dependencies:
            report_content += f"- {dep}\n"
        report_content += "\n"
        
        metrics = {"bugs_fixed": 0, "smells_improved": 0, "security_fixed": 0}
        for entry in self.reports:
            report_content += f"## File: {entry['file']}\n"
            report_content += "### Analysis Results\n"
            for key, value in entry['analysis'].items():
                report_content += f"- **{key}**: {value}\n"
                if key == "bugs" and value:
                    metrics["bugs_fixed"] += len(value)
                if key == "code_smells" and value:
                    metrics["smells_improved"] += len(value)
            report_content += "\n### Before vs After\n"
            report_content += f"**Before**:\n```python\n{entry['before'][:200]}...\n```\n"
            report_content += f"**After**:\n```python\n{entry['after'][:200]}...\n```\n"
            report_content += f"**Diff**:\n```diff\n{''.join(entry['diff'][:10])}\n```\n\n"
        
        report_content += "## Quality Metrics\n"
        report_content += f"- Bugs fixed: {metrics['bugs_fixed']}\n"
        report_content += f"- Code smells improved: {metrics['smells_improved']}\n"
        report_content += f"- Security issues noted: {metrics['security_fixed']}\n"
        
        report_path = os.path.join(self.reports_dir, f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return report_path
