#!/usr/bin/python3
"""
Converting Markdown to HTML
"""
import sys
import os


def parse_heading(line):
    """Convert a Markdown heading to HTML."""
    heading_level = len(line.split(' ')[0])
    if heading_level <= 6:
        heading_text = line[heading_level:].strip()
        return f"<h{heading_level}>{heading_text}</h{heading_level}>\n"
    return ""


def parse_unordered_list_item(line):
    """Convert a Markdown unordered list item to HTML."""
    list_item = line[2:].strip()
    return f"    <li>{list_item}</li>\n"


def parse_ordered_list_item(line):
    """Convert a Markdown ordered list item to HTML."""
    list_item = line[2:].strip()
    return f"    <li>{list_item}</li>\n"


def parse_paragraph(line):
    """Convert a Markdown paragraph to HTML."""
    return f"<p>{line}</p>\n"


def convert_markdown_line(line, in_ulist, in_olist):
    """Convert a single line of Markdown to HTML based on its content."""
    line = line.strip()

    # Check for headings
    if line.startswith('#'):
        # Close the list if we're inside one
        if in_ulist:
            return parse_heading(line), False, in_olist, "</ul>\n"
        if in_olist:
            return parse_heading(line), in_ulist, False, "</ol>\n"
        return parse_heading(line), in_ulist, in_olist, ""

    # Check for unordered lists (- syntax)
    elif line.startswith('- '):
        if not in_ulist:
            if in_olist:
                return (
                    parse_unordered_list_item(line),
                    True, False, "</ol>\n<ul>\n")
            return parse_unordered_list_item(line), True, in_olist, "<ul>\n"
        return parse_unordered_list_item(line), in_ulist, in_olist, ""

    # Check for ordered lists (* syntax)
    elif line.startswith('* '):
        if not in_olist:
            if in_ulist:
                return (
                    parse_ordered_list_item(line),
                    False, True, "</ul>\n<ol>\n")
            return parse_ordered_list_item(line), in_ulist, True, "<ol>\n"
        return parse_ordered_list_item(line), in_ulist, in_olist, ""

    # Treat as a paragraph if it's not empty
    else:
        # Close any open lists
        if in_ulist:
            return parse_paragraph(line), False, in_olist, "</ul>\n"
        if in_olist:
            return parse_paragraph(line), in_ulist, False, "</ol>\n"
        return parse_paragraph(line), in_ulist, in_olist, ""


def convert_markdown_to_html(input_file, output_file):
    """Main function to convert a Markdown file to HTML."""
    try:
        with open(input_file, 'r') as markdown_file:
            html_content = ""
            in_ulist = False  # Currently inside an unordered list?
            in_olist = False  # Currently inside an ordered list?

            for line in markdown_file:
                (c_line, in_ulist,
                 in_olist, list_closer) = convert_markdown_line(
                    line, in_ulist, in_olist)
                html_content += list_closer + c_line

            # Close any unclosed lists at the end of the file
            if in_ulist:
                html_content += "</ul>\n"
            if in_olist:
                html_content += "</ol>\n"

        # Write the generated HTML to the output file
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
