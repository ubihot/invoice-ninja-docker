#!/usr/bin/env python3

import os
import sys
import argparse
import glob
from typing import List, Optional

def read_file_content(file_path: str) -> Optional[str]:
    """Read and return the content of a file, with error handling"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        print(f"Warning: {file_path} is not a text file or uses an unsupported encoding", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

def concatenate_files(files: List[str], output_file: str, add_headers: bool = True) -> bool:
    """Concatenate the contents of selected files into an output file."""
    try:
        with open(output_file, "w", encoding="utf-8") as out:
            for file in files:
                if not os.path.isfile(file):
                    print(f"Warning: {file} does not exist, skipping", file=sys.stderr)
                    continue
                    
                content = read_file_content(file)
                if content is not None:
                    if add_headers:
                        # Add a clear separator and file name header
                        separator = f"\n{'=' * 80}\n"
                        header = f"FILE: {file}\n{'-' * (len(file) + 6)}\n"
                        out.write(f"{separator}{header}")
                    
                    # Write the file content
                    out.write(content)
                    
                    # Add a new line if file doesn't end with one
                    if content and not content.endswith("\n"):
                        out.write("\n")
        return True
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        return False

def expand_file_patterns(patterns: List[str]) -> List[str]:
    """Expand glob patterns and return list of actual files"""
    expanded_files = []
    for pattern in patterns:
        if '*' in pattern or '?' in pattern or '[' in pattern:
            # Use glob to expand wildcards
            matches = glob.glob(pattern)
            if matches:
                expanded_files.extend(matches)
            else:
                print(f"Warning: No files match pattern '{pattern}'", file=sys.stderr)
        else:
            # Regular file path
            expanded_files.append(pattern)
    return expanded_files

def main():
    """Main entry point for contextllm command."""
    parser = argparse.ArgumentParser(
        description="Concatenate multiple files into a single output file with optional headers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  contextllm file1.py file2.py file3.py
  contextllm *.py -o combined.txt
  contextllm src/*.c include/*.h --no-headers
  contextllm -f filelist.txt -o output.txt
  
File list format (for -f option):
  # This is a comment - will be ignored
  src/main.py
  src/utils.py
  # Another comment
  tests/test_main.py
        """
    )
    
    parser.add_argument("files", nargs="*", help="Files to concatenate (supports wildcards like *.py)")
    parser.add_argument("-o", "--output", type=str, default="llm_context.txt", 
                       help="Output file name (default: llm_context.txt)")
    parser.add_argument("--no-headers", action="store_true", 
                       help="Do not add file headers in the output")
    parser.add_argument("-f", "--file-list", type=str, 
                       help="Read list of files from a file (one file per line)")
    
    args = parser.parse_args()
    
    files_to_concatenate = []
    
    # Get files from file list if provided
    if args.file_list:
        try:
            with open(args.file_list, "r", encoding="utf-8") as f:
                line_number = 0
                for line in f:
                    line_number += 1
                    stripped_line = line.strip()
                    
                    # Skip empty lines
                    if not stripped_line:
                        continue
                    
                    # Skip comment lines (starting with #)
                    if stripped_line.startswith("#"):
                        continue
                    
                    files_to_concatenate.append(stripped_line)
                    
            print(f"Read {len(files_to_concatenate)} files from {args.file_list}")
        except FileNotFoundError:
            print(f"Error: File list '{args.file_list}' not found", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error reading file list from {args.file_list}: {e}", file=sys.stderr)
            return 1
    
    # Get files from command line arguments
    if args.files:
        files_to_concatenate.extend(expand_file_patterns(args.files))
    
    # Check if we have any files to process
    if not files_to_concatenate:
        print("Error: No files specified. Use -f to specify a file list or provide files as arguments.", file=sys.stderr)
        parser.print_help()
        return 1
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in files_to_concatenate:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    files_to_concatenate = unique_files
    
    # Check if files exist and filter out non-existent ones
    existing_files = []
    for file in files_to_concatenate:
        if os.path.isfile(file):
            existing_files.append(file)
        else:
            print(f"Warning: {file} does not exist, skipping", file=sys.stderr)
    
    if not existing_files:
        print("Error: No valid files to concatenate.", file=sys.stderr)
        return 1
    
    # Concatenate the files
    print(f"Concatenating {len(existing_files)} files into {args.output}...")
    success = concatenate_files(existing_files, args.output, not args.no_headers)
    
    if success:
        total_size = os.path.getsize(args.output)
        print(f"Success! Created {args.output} ({total_size} bytes)")
        return 0
    else:
        print("Failed to create output file", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())