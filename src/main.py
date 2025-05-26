mport sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import zipfile
import shutil
import git
from analyzer import CodeAnalyzer
from improver import CodeImprover
from output_generator import OutputGenerator
from config import Config

def setup_arguments():
    parser = argparse.ArgumentParser(description="AI Code Review Agent")
    parser.add_argument("input_path", help="Path to codebase (folder, ZIP, or Git URL)")
    parser.add_argument("--output", default="output_codebase", help="Output directory")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    return parser.parse_args()

def clone_git_repo(git_url, extract_to):
    repo_dir = os.path.join(extract_to, "git_repo")
    git.Repo.clone_from(git_url, repo_dir)
    return repo_dir

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def main():
    args = setup_arguments()
    config = Config(args.config)
    
    # Handle input (FR-1.1)
    input_path = args.input_path
    temp_dir = None
    if input_path.endswith('.zip'):
        temp_dir = "temp_extracted_codebase"
        input_path = extract_zip(input_path, temp_dir)
    elif input_path.startswith(('http://', 'https://', 'git@')):
        temp_dir = "temp_git_codebase"
        input_path = clone_git_repo(input_path, temp_dir)
    
    # Validate input directory (FR-1.1, FR-1.2)
    if not os.path.isdir(input_path):
        raise ValueError("Input path must be a valid directory, ZIP, or Git URL")
    
    # Identify code files and project structure (FR-1.3, FR-1.4)
    code_files = []
    supported_extensions = {'.py': 'python', '.js': 'javascript', '.java': 'java'}
    dependencies = []
    for root, dirs, files in os.walk(input_path):
        if any(exclude in root for exclude in config.get("exclude")):
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                code_files.append((os.path.join(root, file), supported_extensions[ext]))
            elif file in ('requirements.txt', 'package.json', 'pom.xml'):
                dependencies.append(os.path.join(root, file))
    
    if not code_files:
        raise ValueError("No supported code files (.py, .js, .java) found")
    
    # Initialize components
    analyzer = CodeAnalyzer(config)
    improver = CodeImprover(config)
    output_gen = OutputGenerator(config, args.output)
    
    # Process files
    for file_path, lang in code_files:
        analysis_results = analyzer.analyze_file(file_path, lang)
        improved_code = improver.improve_code(file_path, analysis_results, lang)
        output_gen.save_improved_code(file_path, improved_code, analysis_results)
    
    # Generate report (FR-4.3, FR-4.4, FR-4.6)
    report_path = output_gen.generate_report(dependencies)
    
    # Clean up
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    print(f"Processing complete. Report generated at: {report_path}")

if __name__ == "__main__":
    main()