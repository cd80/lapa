#!/usr/bin/env python3
"""
Build script for tree-sitter grammars.

This script handles the building and setup of tree-sitter grammars for
different programming languages supported by LAPA.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

PARSER_H_CONTENT = '''
#ifndef TREE_SITTER_PARSER_H_
#define TREE_SITTER_PARSER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#define ts_builtin_sym_error ((TSSymbol)-1)
#define ts_builtin_sym_end 0
#define TREE_SITTER_SERIALIZATION_BUFFER_SIZE 1024

typedef uint16_t TSSymbol;
typedef uint16_t TSFieldId;
typedef struct TSLanguage TSLanguage;

typedef struct {
  TSFieldId field_id;
  uint8_t child_index;
  bool inherited;
} TSFieldMapEntry;

typedef struct {
  uint16_t index;
  uint16_t length;
} TSFieldMapSlice;

typedef struct {
  bool visible;
  bool named;
  bool supertype;
} TSSymbolMetadata;

typedef struct TSLexer TSLexer;

struct TSLexer {
  int32_t lookahead;
  TSSymbol result_symbol;
  void (*advance)(TSLexer *, bool);
  void (*mark_end)(TSLexer *);
  uint32_t (*get_column)(TSLexer *);
  bool (*is_at_included_range_start)(const TSLexer *);
  bool (*eof)(const TSLexer *);
};

typedef enum {
  TSParseActionTypeShift,
  TSParseActionTypeReduce,
  TSParseActionTypeAccept,
  TSParseActionTypeRecover,
} TSParseActionType;

typedef union {
  struct {
    uint8_t type;
    TSStateId state;
    bool extra;
  } shift;
  struct {
    uint8_t type;
    uint8_t child_count;
    TSSymbol symbol;
    int16_t dynamic_precedence;
    uint16_t production_id;
  } reduce;
  uint8_t type;
} TSParseAction;

typedef struct {
  uint16_t lex_state;
  uint16_t external_lex_state;
} TSLexMode;

typedef union {
  TSParseAction action;
  struct {
    uint8_t count;
    bool reusable;
  } entry;
} TSParseActionEntry;

typedef struct TSStateId {
  uint16_t value;
} TSStateId;

typedef struct {
  const TSLanguage *language;

  const bool *valid_external_tokens;
  const TSSymbol *external_scanner_symbol_map;
  void *external_scanner_states;
  void *external_scanner_state;
  const TSFieldMapSlice *field_map_slices;
  const TSFieldMapEntry *field_map_entries;
  const char **field_names;
  const TSFieldMapSlice *alias_map;
  const uint16_t *alias_sequences;

  uint32_t version;
  TSSymbol *symbol_names;
  const TSSymbolMetadata *symbol_metadata;
  const TSParseActionEntry *parse_table;
  const TSLexMode *lex_modes;
  uint16_t state_count;
  uint16_t large_state_count;
  uint16_t symbol_count;
  uint16_t field_count;
  uint16_t alias_count;
  uint16_t token_count;
  uint16_t external_token_count;
  uint16_t max_alias_sequence_length;
  uint16_t parse_action_count;
} TSParser;

typedef struct {
  const void *payload;
  const char *name;
} TSExternalTokenType;

typedef struct {
  void *(*create)(void);
  void (*destroy)(void *);
  bool (*scan)(void *, TSLexer *, const bool *valid_symbols);
  unsigned (*serialize)(void *, char *);
  void (*deserialize)(void *, const char *, unsigned);
} TSExternalScanner;

typedef struct {
  const TSExternalTokenType *types;
  uint32_t count;
  TSExternalScanner scanner;
} TSExternalScannerState;

#ifdef __cplusplus
}
#endif

#endif  // TREE_SITTER_PARSER_H_
'''

def run_command(cmd: list[str], cwd: Optional[Path] = None, env: Optional[dict] = None) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})}
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return False

def ensure_tree_sitter_cli():
    """Ensure tree-sitter CLI is installed."""
    try:
        subprocess.run(["tree-sitter", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print("tree-sitter CLI not found. Installing...", file=sys.stderr)
        if not run_command(["npm", "install", "-g", "tree-sitter-cli"]):
            print("Failed to install tree-sitter CLI. Please install manually:", file=sys.stderr)
            print("npm install -g tree-sitter-cli", file=sys.stderr)
            return False
        return True
    except subprocess.CalledProcessError:
        print("Error checking tree-sitter CLI version", file=sys.stderr)
        return False

def setup_grammar_repo(name: str, url: str) -> Optional[Path]:
    """Clone or update a grammar repository."""
    grammar_dir = Path("build") / f"tree-sitter-{name}"
    
    if grammar_dir.exists():
        print(f"Updating {name} grammar...")
        if not run_command(["git", "pull"], cwd=grammar_dir):
            return None
    else:
        print(f"Cloning {name} grammar...")
        if not run_command(["git", "clone", url, str(grammar_dir)]):
            return None
    
    return grammar_dir

def setup_tree_sitter_headers():
    """Set up tree-sitter header files."""
    headers_dir = Path("lib") / "include" / "tree_sitter"
    headers_dir.mkdir(parents=True, exist_ok=True)
    
    # Create parser.h
    parser_h = headers_dir / "parser.h"
    try:
        with open(parser_h, 'w') as f:
            f.write(PARSER_H_CONTENT)
        return True
    except Exception as e:
        print(f"Error creating parser.h: {e}", file=sys.stderr)
        return False

def build_grammar(grammar_dir: Path) -> bool:
    """Build a grammar in the specified directory."""
    print(f"Building grammar in {grammar_dir}...")
    if not run_command(["tree-sitter", "generate"], cwd=grammar_dir):
        return False
    
    # Create lib directory
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)
    
    # Copy parser source
    src = grammar_dir / "src" / "parser.c"
    if not src.exists():
        print(f"Parser source not found: {src}", file=sys.stderr)
        return False
    
    try:
        # Copy parser files
        parser_c = lib_dir / f"{grammar_dir.name}-parser.c"
        shutil.copy2(src, parser_c)
        
        scanner_c = grammar_dir / "src" / "scanner.c"
        if scanner_c.exists():
            shutil.copy2(scanner_c, lib_dir / f"{grammar_dir.name}-scanner.c")
        
        # Build shared library
        include_path = str(Path("lib") / "include")
        if sys.platform == "darwin":
            output = lib_dir / f"{grammar_dir.name}.dylib"
            cmd = [
                "cc",
                "-fPIC",
                "-shared",
                f"-I{include_path}",
                "-o", str(output),
                str(parser_c)
            ]
        else:
            output = lib_dir / f"{grammar_dir.name}.so"
            cmd = [
                "cc",
                "-fPIC",
                "-shared",
                f"-I{include_path}",
                "-o", str(output),
                str(parser_c)
            ]
        
        if not run_command(cmd):
            return False
        
        return True
    except Exception as e:
        print(f"Error building parser library: {e}", file=sys.stderr)
        return False

def build_javascript_grammar():
    """Build the JavaScript grammar."""
    try:
        # Create build directory
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        # Setup JavaScript grammar repository
        grammar_dir = setup_grammar_repo(
            "javascript",
            "https://github.com/tree-sitter/tree-sitter-javascript.git"
        )
        if not grammar_dir:
            return False
        
        # Setup tree-sitter headers
        if not setup_tree_sitter_headers():
            return False
        
        # Build the grammar
        if not build_grammar(grammar_dir):
            return False
        
        print("Successfully built JavaScript grammar")
        return True
    except Exception as e:
        print(f"Error building JavaScript grammar: {e}", file=sys.stderr)
        return False

def main():
    """Main entry point for grammar building."""
    print("Setting up tree-sitter grammars...")
    
    # Ensure tree-sitter CLI is available
    if not ensure_tree_sitter_cli():
        sys.exit(1)
    
    # Build JavaScript grammar
    if not build_javascript_grammar():
        print("Failed to build JavaScript grammar", file=sys.stderr)
        sys.exit(1)
    
    print("Successfully built all grammars")

if __name__ == "__main__":
    main()
