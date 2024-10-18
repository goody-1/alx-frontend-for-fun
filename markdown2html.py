#!/usr/bin/python3
"""
Converting Markdown to HTML
"""
import sys
import os


def convert_markdown_to_html(input_file, output_file):
    """Function to convert markdown to HTML"""
    try:
        with open(input_file, 'r') as markdown_file:
            html_content = ""
            for line in markdown_file:
                line = line.strip()
                
                # Parse Markdown headings and convert them to HTML
                if line.startswith('#'):
                    # Count the number of '#' to determine heading level
                    heading_level = len(line.split(' ')[0])
                    if heading_level <= 6:
                        heading_text = line[heading_level:].strip()
                        html_content += f"<h{heading_level}>{heading_text}</h{heading_level}>\n"
                else:
                    # Add other non-heading lines as raw paragraphs
                    if line:  # only add paragraph tags if line is not empty
                        html_content += f"<p>{line}</p>\n"

        with open(output_file, 'w') as html_file:
            html_file.write(html_content)

    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

def main():
    """The entry to the program"""
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    convert_markdown_to_html(input_file, output_file)
    sys.exit(0)


if __name__ == "__main__":
    main()
