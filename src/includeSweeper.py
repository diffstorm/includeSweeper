"""
includeSweeper.py

This script checks for and lists redundant include statements in a C/C++ project.
It parses command-line arguments to specify the project path and the compilation command.
It then compiles the project and iteratively removes each include statement to check for compilation errors.
The script reports any redundant includes along with their file paths and line numbers in a table.

Usage:
python includeSweeper.py --path [project_path] --cmd [compile_command]

Example:
python includeSweeper.py --path "path/to/project" --cmd "make all"
python includeSweeper.py --path "path/to/project" --cmd "gcc src/main.c"

Dependencies:
- Python 3.x
- tabulate package (install using 'pip install tabulate')

Author: Eray Ozturk | erayozturk1@gmail.com 
URL: github.com/diffstorm
Date: 15/05/2024

"""

import os
import re
import subprocess
import argparse
import shutil
from tabulate import tabulate

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
    - args: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Find redundant includes.")
    parser.add_argument("--path", required=True, help="Path to the project.")
    parser.add_argument("--cmd", required=True, help="Command to compile the project.")
    args = parser.parse_args()

    # Normalize the path for the current operating system
    args.path = os.path.abspath(args.path)

    return args

def get_files(path, extensions):
    """
    Get a list of files with specified extensions in a directory and its subdirectories.

    Args:
    - path (str): Path to the directory.
    - extensions (list of str): List of file extensions to search for.

    Returns:
    - files (list of str): List of file paths.
    """
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def compile_project(cmd, work_dir):
    """
    Compile the project and capture the output.

    Args:
    - cmd (str): Command to compile the project.
    - work_dir (str): Working directory for the compilation.

    Returns:
    - returncode (int): Return code of the compilation process.
    - stdout (str): Standard output of the compilation process.
    - stderr (str): Standard error of the compilation process.
    """
    result = subprocess.run(cmd, shell=True, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode(), result.stderr.decode()

def count_errors_and_warnings(output):
    """
    Count the number of errors and warnings in the compilation output.

    Args:
    - output (str): Compilation output (stdout and stderr combined).

    Returns:
    - error_count (int): Number of errors.
    - error_lines (list of str): Lines containing errors or warnings.
    """
    error_lines = [line for line in output.split('\n') if "error:" in line or "warning:" in line]
    return len(error_lines), error_lines

def find_include_line(include, lines, include_pattern):
    """
    Find the line number of an include statement in the code.

    Args:
    - include (str): Include statement to find.
    - lines (list of str): Lines of code.
    - include_pattern (str): Regular expression pattern for matching include statements.

    Returns:
    - include_line_index (int or None): Line number of the include statement, or None if not found.
    """
    include_line_index = None
    for index, line in enumerate(lines):
        if re.match(include_pattern.format(re.escape(include)), line):
            include_line_index = index
            break
    return include_line_index

def remove_line_and_compile(file, cmd, work_dir, line_index):
    """
    Remove a line from a file, compile the project, and check for errors.

    Args:
    - file (str): Path to the file.
    - cmd (str): Command to compile the project.
    - work_dir (str): Working directory for the compilation.
    - line_index (int): Index of the line to remove.

    Returns:
    - error_count (int): Number of errors in the compilation output.
    - error_lines (list of str): Lines containing errors or warnings in the compilation output.
    - line_number (int): Line number of the removed line (1-based).
    """
    # Create a backup of the current file
    temp_file = file + '.bak'
    shutil.copyfile(file, temp_file)

    with open(file, 'r') as f:
        lines = f.readlines()

    original_line = lines[line_index]
    del lines[line_index]
    with open(file, 'w') as f:
        f.writelines(lines)
    
    returncode, stdout, stderr = compile_project(cmd, work_dir)
    error_count, error_lines = count_errors_and_warnings(stdout + stderr)
    
    # Restore the file from the backup
    shutil.copyfile(temp_file, file)
    # Remove the backup file
    os.remove(temp_file)
    
    return error_count, error_lines, line_index + 1  # Return line number (1-based)

def remove_comments(code):
    """
    Remove C/C++ comments from the code while preserving line numbers by replacing comment parts with empty spaces.

    Args:
    - code (list of str): List of lines of code.

    Returns:
    - code_without_comments (list of str): List of lines with comments removed.
    """
    code_without_comments = []
    in_block_comment = False

    for line in code:
        if in_block_comment:
            clean_line = ''
        else:
            clean_line = ''

        i = 0
        while i < len(line):
            if not in_block_comment:
                if line[i:i+2] == '/*':
                    in_block_comment = True
                    clean_line += ' ' * (len(line) - i)  # Replace the rest of the line with spaces
                    i += 1
                elif line[i:i+2] == '//':
                    clean_line += ' ' * (len(line) - i)  # Replace the rest of the line with spaces
                    break
                else:
                    clean_line += line[i]
            else:
                if line[i:i+2] == '*/':
                    in_block_comment = False
                    i += 1
            i += 1

        if not in_block_comment and '//' not in line:
            code_without_comments.append(clean_line)
        else:
            code_without_comments.append(clean_line.rstrip())

    return code_without_comments

def main():
    args = parse_arguments()
    path = args.path
    cmd = args.cmd

    # Check if the path exists
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist.")
        return

    # Change to the provided path
    original_dir = os.getcwd()
    os.chdir(path)

    try:
        # Check if the project compiles successfully before modifications
        print("Checking initial compilation...")
        base_returncode, base_stdout, base_stderr = compile_project(cmd, os.getcwd())
        if base_returncode != 0:
            print("Error: The project does not compile successfully without modifications.")
            print(base_stdout)
            print(base_stderr)
            return

        base_error_count, base_error_lines = count_errors_and_warnings(base_stdout + base_stderr)
        
        extensions = ['.c', '.cpp', '.h', '.hpp']
        files = get_files(path, extensions)

        redundant_includes = {}

        include_pattern = r'#\s*include\s*[<"]{}[">]'

        print("Processing files...")
        for file in files:
            with open(file, 'r') as f:
                lines = remove_comments(f.readlines())

            includes = [re.findall(include_pattern.format(r'(.*)'), line) for line in lines]
            includes = [item for sublist in includes for item in sublist]

            for include in includes:
                include_line_index = find_include_line(include, lines, include_pattern)    
                if include_line_index is not None:
                    error_count, error_lines, line_number = remove_line_and_compile(file, cmd, os.getcwd(), include_line_index)
                    if error_count <= base_error_count:
                        if file not in redundant_includes:
                            redundant_includes[file] = []
                        redundant_includes[file].append((include, line_number))

        table_data = []
        for file, includes in redundant_includes.items():
            for include, line_number in includes:
                # Get the relative path from the provided --path
                relative_path = os.path.relpath(file, start=path)
                table_data.append([include, relative_path, line_number])

        print(f"Directory: {path}")
        if table_data:
            print("\nRedundant Includes:")
            print(tabulate(table_data, headers=["Include", "File", "Line"], showindex=True, tablefmt="grid"))
        else:
            print("\nNo redundant includes found.")

    finally:
        # Change back to the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()
