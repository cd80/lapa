#!/usr/bin/env python3

import os
import subprocess
import sys
from tree_sitter import Language

def run_command(command, cwd=None):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode().strip()
        print(f"Command '{' '.join(command)}' failed with error: {stderr_output}")
        sys.exit(1)

# Languages specified in README.md
languages = {
    'python': 'https://github.com/tree-sitter/tree-sitter-python',
    'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript',
    'typescript': 'https://github.com/tree-sitter/tree-sitter-typescript',
    'c': 'https://github.com/tree-sitter/tree-sitter-c',
    'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp',
    'rust': 'https://github.com/tree-sitter/tree-sitter-rust',
    'java': 'https://github.com/tree-sitter/tree-sitter-java',
}

dest_dir = os.path.join(os.path.dirname(__file__), '..', 'lapa', 'frontends', 'grammars')
os.makedirs(dest_dir, exist_ok=True)

grammar_dirs = []

# Clone or update the grammar repositories
for lang, repo in languages.items():
    print(f"\nProcessing {lang}...")
    lang_dir = os.path.join(dest_dir, f"tree-sitter-{lang}")
    if not os.path.exists(lang_dir):
        # Clone the repository
        run_command(['git', 'clone', repo, lang_dir])
    else:
        # Pull the latest changes
        run_command(['git', '-C', lang_dir, 'pull'])

    # Install npm dependencies if package.json exists
    package_json = os.path.join(lang_dir, 'package.json')
    if os.path.exists(package_json):
        print(f"Installing npm dependencies in {lang_dir}...")
        run_command(['npm', 'install'], cwd=lang_dir)

    # Special handling for TypeScript subgrammars
    if lang == 'typescript':
        subgrammars = ['typescript', 'tsx']
        for sub_lang in subgrammars:
            grammar_dir = os.path.join(lang_dir, sub_lang)
            print(f"Processing {lang} ({sub_lang}) grammar...")

            if not os.path.exists(grammar_dir):
                print(f"Grammar directory {grammar_dir} does not exist.")
                continue

            # Install npm dependencies in subdirectory if package.json exists
            package_json = os.path.join(grammar_dir, 'package.json')
            if os.path.exists(package_json):
                print(f"Installing npm dependencies in {grammar_dir}...")
                run_command(['npm', 'install'], cwd=grammar_dir)

            # Generate parser
            run_command(['tree-sitter', 'generate'], cwd=grammar_dir)

            # Add the grammar directory to the list
            grammar_dirs.append(grammar_dir)
    else:
        # Generate parser
        run_command(['tree-sitter', 'generate'], cwd=lang_dir)

        # Add the grammar directory to the list
        grammar_dirs.append(lang_dir)

# Set CC environment variable to include '-std=c11'
os.environ['CC'] = 'cc -std=c11'

# Build the shared library
so_path = os.path.join(dest_dir, 'build', 'languages.so')
os.makedirs(os.path.dirname(so_path), exist_ok=True)
print("\nBuilding shared library...")
Language.build_library(
    # Output path
    so_path,
    # List of grammar directories
    grammar_dirs
)

print("\nAll grammars have been built into a shared library successfully.")
