#!/usr/bin/python3
"""
Converting Markdown to HTML
"""
import sys
import os
import re
import hashlib


def parse_heading(line):
    """Convert a Markdown heading to HTML (supports heading levels 1 to 6)."""
    heading_level = len(line.split(' ')[0])
    if 1 <= heading_level <= 6:  # Check for heading levels between 1 and 6
        heading_text = line[heading_level:].strip()
        return f"<h{heading_level}>\
{parse_custom_syntax(heading_text)}</h{heading_level}>\n"
    return ""


def parse_unordered_list_item(line):
    """Convert a Markdown unordered list item to HTML."""
    list_item = line[2:].strip()
    return f"<li>{parse_custom_syntax(list_item)}</li>\n"


def parse_ordered_list_item(line):
    """Convert a Markdown ordered list item to HTML."""
    list_item = line[2:].strip()
    return f"<li>{parse_custom_syntax(list_item)}</li>\n"


def parse_paragraph(lines):
    """Convert multiple lines of Markdown text into a single HTML paragraph."""
    paragraph = "<p>\n" + "<br/>\n".join(
        [parse_custom_syntax(line) for line in lines]) + "\n</p>\n"
    return paragraph


def parse_bold_and_italics(text):
    """Convert Markdown bold (**) and italics (__) to HTML <b> and <em>."""
    # Bold (**text** -> <b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italics (__text__ -> <em>text</em>)
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    return text


def convert_md5(text):
    """Convert text inside [[ ]] to MD5 hash."""
    return hashlib.md5(text.encode()).hexdigest()


def remove_c(text):
    """Remove all 'c' (case insensitive) from the text inside (( ))."""
    return re.sub(r'[cC]', '', text)


def parse_custom_syntax(text):
    """Parse custom syntax for MD5 hashing ([[ ]]) and removing 'c' (( ))."""
    # Convert text inside [[ ]] to its MD5 hash
    text = re.sub(r'\[\[(.*?)\]\]',
                  lambda match: convert_md5(match.group(1)), text)
    # Remove 'c' (case insensitive) from text inside (( ))
    text = re.sub(r'\(\((.*?)\)\)',
                  lambda match: remove_c(match.group(1)), text)

    # Then apply the bold and italics transformations
    text = parse_bold_and_italics(text)

    return text


def convert_markdown_line(line, in_ulist, in_olist, in_paragraph):
    """Convert a single line of Markdown to HTML based on its content."""
    line = line.rstrip()

    # Check for headings (supports heading levels 1 to 6)
    if line.startswith('#'):
        heading_level = len(line.split(' ')[0])
        if 1 <= heading_level <= 6:
            # Close any lists if we're inside one
            if in_ulist:
                return parse_heading(line), False, in_olist, False, "</ul>\n"
            if in_olist:
                return parse_heading(line), in_ulist, False, False, "</ol>\n"
            return parse_heading(line), in_ulist, in_olist, False, ""

    # Check for unordered lists (- syntax)
    elif line.startswith('- '):
        if not in_ulist:
            if in_olist:
                return (parse_unordered_list_item(line), True,
                        False, False, "</ol>\n<ul>\n")
            return (parse_unordered_list_item(line), True,
                    in_olist, False, "<ul>\n")
        return (parse_unordered_list_item(line), in_ulist,
                in_olist, False, "")

    # Check for ordered lists (* syntax)
    elif line.startswith('* '):
        if not in_olist:
            if in_ulist:
                return (parse_ordered_list_item(line), False,
                        True, False, "</ul>\n<ol>\n")
            return (parse_ordered_list_item(line), in_ulist,
                    True, False, "<ol>\n")
        return (parse_ordered_list_item(line), in_ulist,
                in_olist, False, "")

    # Treat as paragraph text if it's not empty
    elif line:
        if in_ulist:
            return line, False, in_olist, True, "</ul>\n"
        if in_olist:
            return line, in_ulist, False, True, "</ol>\n"
        return line, in_ulist, in_olist, True, ""

    # If it's an empty line, it may indicate the end of a paragraph
    else:
        if in_paragraph:
            return "", in_ulist, in_olist, False, ""  # Close the paragraph
        return "", in_ulist, in_olist, False, ""  # Just skip empty lines


def convert_markdown_to_html(input_file, output_file):
    """Main function to convert a Markdown file to HTML."""
    try:
        with open(input_file, 'r') as markdown_file:
            html_content = ""
            in_ulist = False  # Track if we're inside an unordered list
            in_olist = False  # Track if we're inside an ordered list
            in_paragraph = False  # Track if we're inside a paragraph
            paragraph_lines = []  # Hold lines that make up a paragraph

            for line in markdown_file:
                (converted_line, in_ulist, in_olist, in_paragraph_active,
                    list_closer) = convert_markdown_line(
                        line, in_ulist, in_olist, in_paragraph)

                # Close list if needed
                if list_closer:
                    html_content += list_closer

                # Handle paragraphs
                if in_paragraph_active:
                    paragraph_lines.append(parse_custom_syntax(converted_line))

                # If transitioning out of a paragraph (empty line or end)
                if in_paragraph and not in_paragraph_active:
                    html_content += parse_paragraph(paragraph_lines)
                    paragraph_lines = []

                in_paragraph = in_paragraph_active

                # If it's a heading or list, append it directly
                if not in_paragraph_active and converted_line:
                    html_content += converted_line

            # Close any open paragraph at the end of the file
            if in_paragraph:
                html_content += parse_paragraph(paragraph_lines)

            # Close any open unordered list at the end of the file
            if in_ulist:
                html_content += "</ul>\n"

            # Close any open ordered list at the end of the file
            if in_olist:
                html_content += "</ol>\n"

        with open(output_file, 'w') as html_file:
            html_file.write(html_content)

    except FileNotFoundError:
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)


def main():
    """Handle command-line arguments and trigger the Markdown conversion."""
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
    """Main context"""
    main()
