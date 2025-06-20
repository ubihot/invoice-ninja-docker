#!/usr/bin/env python3

import os
import sys
import argparse
from typing import List

def list_files(directory: str, recursive: bool, exclude_patterns: List[str] = None, 
               include_hidden: bool = False) -> List[str]:
    """
    List files in the directory with optional filtering.
    Returns relative paths from the given directory.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    result_files = []

    if recursive:
        # Walk through directory tree for recursive listing
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories if not including hidden files
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                # Skip hidden files if not including them
                if not include_hidden and file.startswith("."):
                    continue

                # Skip excluded patterns
                if any(pattern in file for pattern in exclude_patterns):
                    continue

                # Get path relative to starting directory
                rel_path = os.path.join(os.path.relpath(root, directory), file)
                if rel_path.startswith("./"):
                    rel_path = rel_path[2:]
                elif rel_path == ".":
                    rel_path = file
                result_files.append(rel_path)
    else:
        # Non-recursive listing
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)

                # Skip directories
                if os.path.isdir(full_path):
                    continue

                # Skip hidden files if not including them
                if not include_hidden and item.startswith("."):
                    continue

                # Skip excluded patterns
                if any(pattern in item for pattern in exclude_patterns):
                    continue

                result_files.append(item)
        except Exception as e:
            print(f"Error listing directory {directory}: {e}", file=sys.stderr)
            return []

    return sorted(result_files)

def write_listed_files_to_file(files: List[str], output_file: str) -> None:
    """Write list of files to output file"""
    try:
        with open(output_file, "w", encoding="utf-8") as out:
            for file_name in files:
                out.write(f"{file_name}\n")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for listllm command."""
    parser = argparse.ArgumentParser(
        description="List files in a directory with filtering options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  listllm                           # List files in current directory
  listllm -d /path/to/dir          # List files in specific directory
  listllm -r                       # List files recursively
  listllm --exclude .pyc .git      # Exclude patterns
  listllm --include-hidden         # Include hidden files
  listllm -o files.txt             # Write output to file
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".", 
                       help="Directory to list files from (default: current directory)")
    parser.add_argument("-r", "--recursive", action="store_true", 
                       help="List files recursively from subdirectories")
    parser.add_argument("--include-hidden", action="store_true", 
                       help="Include hidden files (starting with .)")
    parser.add_argument("--exclude", type=str, nargs="+", default=[], 
                       help="Patterns to exclude files (e.g., .pyc .git __pycache__)")
    parser.add_argument("-o", "--output", type=str, 
                       help="Write list to file instead of stdout")
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        return 1
    
    # List files
    files = list_files(
        args.directory,
        args.recursive,
        exclude_patterns=args.exclude,
        include_hidden=args.include_hidden
    )
    
    if not files:
        print(f"No files found in {args.directory}")
        return 0
    
    # Output the list (either to file or stdout)
    if args.output:
        write_listed_files_to_file(files, args.output)
        print(f"Listed {len(files)} files to {args.output}")
    else:
        for file in files:
            print(file)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())