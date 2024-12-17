import argparse
import re
import csv
import sys
from typing import Dict, Optional, List

class ARM2AssemblyConverter:

    labels = {}

    def __init__(self, 
                 csv_path: str, 
                 wrap_comments: bool = True,
                 comment_prefix: str = ';',
                 case_sensitive: bool = False):
        """
        Initialize the ARM2 Assembly Converter
        
        :param csv_path: Path to the CSV file with opcode information
        :param wrap_comments: Whether to wrap comments in spans
        :param comment_prefix: Character(s) used to denote comments
        :param case_sensitive: Whether mnemonic matching is case-sensitive
        """
        # Explicitly set instance attributes
        self.wrap_comments = wrap_comments
        self.comment_prefix = comment_prefix
        self.case_sensitive = case_sensitive
        
        # Load opcode information
        self.opcode_info = self._load_opcode_info(csv_path)
    
    def _load_opcode_info(self, csv_path: str) -> Dict[str, Dict[str, str]]:
        """
        Load opcode and directive information from CSV file.
        
        :param csv_path: Path to the CSV file
        :return: Dictionary mapping mnemonics to their metadata
        """
        opcode_info = {}
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Normalize mnemonic based on case sensitivity
                mnemonic = row['Mnemonic'].upper() if not self.case_sensitive else row['Mnemonic']
                opcode_info[mnemonic] = {
                    'type': row['Category'],
                    'description': row['Description']
                }

        return opcode_info
    
    def convert(self, assembly_code: str) -> str:
        """
        Convert ARM2 assembly code to HTML with spans and anchors.
        
        :param assembly_code: Raw assembly code
        :return: HTML-annotated assembly code
        """
        # First pass: Collect labels
        self.labels = self._collect_labels(assembly_code)

        # Split lines for processing
        lines = assembly_code.split('\n')
        processed_lines = []
        
        for line in lines:
            # Preserve empty lines
            if not line.strip():
                processed_lines.append("<span>"+line+"</span>")
                continue
            
            
            # Handle comments
            comment_split = line.split(self.comment_prefix, 1)
            code_part = comment_split[0]
            comment_part = comment_split[1] if len(comment_split) > 1 else None

            # Fix difficult characters
            code_part = code_part.replace('<', '&lt;')

            # Process code part
            processed_code = self._process_line(code_part, self.labels)
            
            # Process comment part
            if comment_part is not None:
                if self.wrap_comments:
                    comment_part = f'<span class="comment" data-type="Comment">{self.comment_prefix}{comment_part}</span>'
                else:
                    comment_part = f'{self.comment_prefix}{comment_part}'
                processed_line = processed_code + comment_part
            else:
                processed_line = processed_code
            
            
            processed_lines.append("<span>"+processed_line+"</span>")
        
        return '\n'.join(processed_lines)
    
    def _collect_labels(self, assembly_code: str) -> Dict[str, str]:
        """
        Collect all labels in the assembly code.
        
        :param assembly_code: Raw assembly code
        :return: Dictionary mapping labels to their HTML id
        """
        _labels = {}
        for line in assembly_code.split('\n'):
            # Identify labels (ending with ':' and optionally starting with '.')
            label_match = re.match(r'^(\.\w+)', line.strip())
            if label_match:
                label = label_match.group(1).replace(".", "")
                _labels[label] = label
        return _labels
    
    def _process_line(self, line: str, labels: Dict[str, str]) -> str:
        """
        Process a single line of assembly code.
        
        :param line: Line of assembly code
        :param labels: Dictionary of known labels
        :return: Processed line with HTML annotations
        """
        # Split line into parts
        parts = re.split(r'([\s:,#\(\)\"]+)', line)
        processed_parts = []

        for part in parts:
            # Normalize part for checking
            norm_part = part.strip().upper() if not self.case_sensitive else part.strip()
            
            # Check for labels (including point labels)
            label_match = re.match(r'^(\.\w+)', part.strip())
            if label_match:
                label = label_match.group(1).replace(".", "")
                part = f'<span class="label"><a id="{label}" data-type="Label">{part}</a></span>'

            # Check for mnemonics and opcodes
            elif norm_part in self.opcode_info:
                info = self.opcode_info[norm_part]
                part = (f'<span data-type="{info["type"]}" '
                        f'data-description="{info["description"]}"'
                        f'title="{info["description"]}">'
                        f'{part}</span>')
            
            # Check for branch instructions with labels
            elif part in self.labels:
                part = f'<span class="branch"><a data-type="Branch" href="#{part}">{part}</a></span>'

            else:
                part = f'<span>{part}</span>'
            
            processed_parts.append(part)
        
        return ''.join(processed_parts)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Convert ARM2 Assembly to HTML with semantic markup'
    )
    parser.add_argument(
        'input', 
        help='Input assembly file path'
    )
    parser.add_argument(
        'csv', 
        help='CSV file with opcode/directive information'
    )
    parser.add_argument(
        'output', 
        help='Output HTML file path'
    )
    parser.add_argument(
        '--no-comment-wrap', 
        action='store_true', 
        help='Disable wrapping comments in spans'
    )
    parser.add_argument(
        '--comment-prefix', 
        default=';', 
        help='Character(s) used to denote comments (default: ;)'
    )
    parser.add_argument(
        '--case-sensitive', 
        action='store_true', 
        help='Make mnemonic matching case-sensitive'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Read input assembly file
        with open(args.input, 'r') as f:
            assembly_code = f.read()
        
        # Create converter with specified options
        converter = ARM2AssemblyConverter(
            csv_path=args.csv,
            wrap_comments=not args.no_comment_wrap,
            comment_prefix=args.comment_prefix,
            case_sensitive=args.case_sensitive
        )

        # Convert to HTML
        annotated_code = converter.convert(assembly_code)

        options = '<div class="options"><button class="toggle_comments">👁️‍🗨️</button><button class="toggle_night">🌝</button></div>'

        toc = '<div class="toc-wrap"><div class="toc">'
        for label in converter.labels:
            toc += f'<a data-type="Branch" href="#{label}">{label}</a>' 
        toc += '</div></div>'

        html_code = (
            f'<!DOCTYPE html><html lang="en">\n'
            f'<head>\n'
            f'<title>Annotated Source Code: {args.input}</title>\n'
            f'<link rel="stylesheet" href="style.css" />\n'
            f'</head>\n'
            f'{options}\n'
            f'{toc}\n'
            f'<pre id="annotated-code">\n<code>\n'
            f'{annotated_code}\n'
            f'<code>\n</pre>\n'
            f'<script src="script.js"></script>\n'
            f'</html>\n'
        )

        # Write output
        with open(args.output, 'w') as f:
            f.write(html_code)
        
        print(f"Converted {args.input} to {args.output}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
