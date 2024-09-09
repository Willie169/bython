import re
import os

"""
Python module for converting Bython code (C-style syntax) to Python code.

This module includes utilities for renaming files from `.by` to `.py`, 
parsing import statements, converting C-style type declarations to Python 
function definitions, and adjusting code blocks. It also handles translating 
comments from C-style to Python and ensures compatibility by adding `pass` 
statements where needed in empty code blocks.
"""


def _ends_in_by(word):
    """
    Returns True if word ends in .by, else False

    Args:
        word (str): Filename to check

    Returns:
        bool: Whether the 'word' ends with '.by' or not
    """
    if word.endswith(".by"):
        return True
    return False


def _change_file_name(name, outputname=None):
    """
    Changes *.by filenames to *.py filenames. If filename does not end in .by,
    it adds .py to the end.

    Args:
        name (str): Filename to edit
        outputname (str): Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.py at the end (unless 'outputname' is
        specified, then that is returned).
    """
    # If outputname is specified, return that
    if outputname is not None:
        return outputname

    # Otherwise, create a new name
    if _ends_in_by(name):
        return name[:-3] + ".py"
    else:
        return name + ".py"


def parse_imports(filename):
    """
    Reads the file and scans for imports. Returns the assumed filename
    of all the imported modules (i.e., module names appended with ".by").

    Args:
        filename (str): Path to file

    Returns:
        list of str: All imported modules suffixed with '.by'.
    """
    with open(filename, "r") as infile:
        infile_str = infile.read()

    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    imports_with_suffixes = [im + ".by" for im in imports + imports2]

    return imports_with_suffixes


def add_pass_to_empty_blocks(code):
    """
    Adds 'pass' to empty code blocks defined by '{}' in the Bython code.

    Args:
        code (str): The Bython code as a string

    Returns:
        str: The modified code with 'pass' added to empty blocks
    """
    lines = code.split("\n")
    in_multiline_comment = False
    result = []

    for line in lines:
        stripped = line.strip()

        if '"""' in stripped or "'''" in stripped:
            in_multiline_comment = not in_multiline_comment

        if not in_multiline_comment:
            code_part = line.split("#")[0]

            if re.match(r".*{\s*}.*", code_part):
                line = re.sub(
                    r"{\s*}",
                    "{\n"
                    + " " * (len(line) - len(line.lstrip()))
                    + "pass\n"
                    + " " * (len(line) - len(line.lstrip()))
                    + "}",
                    line,
                )

        result.append(line)

    return "\n".join(result)


def convert_c_type_to_python(c_type):
    """
    Converts C-style types to Python types.

    Args:
        c_type (str): C-style type (e.g., 'int', 'float')

    Returns:
        str: Corresponding Python type (e.g., 'int', 'float')
    """
    type_map = {
        "int": "int",
        "float": "float",
        "double": "float",
        "char": "str",
        "void": "None",
        "bool": "bool",
    }
    return type_map.get(c_type, "Any")


def convert_type_declaration(line):
    """
    Converts a C-style function signature into a Python function signature.

    Args:
        line (str): A line of Bython code containing a C-style function declaration

    Returns:
        tuple: A tuple containing the Python-style function definition, a boolean
               indicating whether it is a function definition, and another boolean
               indicating whether it is an empty function (no body).
    """
    pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*(\{)?"
    match = re.match(pattern, line)
    if match:
        return_type, func_name, params, has_body = match.groups()
        params_converted = []
        for param in params.split(","):
            param = param.strip()
            if param:
                param_parts = param.split()
                param_type = " ".join(param_parts[:-1])
                param_name = param_parts[-1]
                python_type = convert_c_type_to_python(param_type)
                params_converted.append(f"{param_name}: {python_type}")
        python_return_type = convert_c_type_to_python(return_type)

        if has_body:
            return (
                f"def {func_name}({', '.join(params_converted)}) -> {python_return_type}:",
                True,
                False,
            )
        else:
            return (
                f"def {func_name}({', '.join(params_converted)}) -> {python_return_type}: pass",
                True,
                True,
            )
    return line, False, False


def parse_file(
    filepath, add_true_line, filename_prefix, outputname=None, change_imports=None
):
    """
    Converts a Bython file to a Python file and writes it to disk.

    Args:
        filepath (str): Path to the Bython file you want to parse.
        add_true_line (bool): Whether to add a line at the top of the
                              file, adding support for C-style true/false
                              in addition to capitalized True/False.
        filename_prefix (str): Prefix to the resulting file name.
        outputname (str): Optional. Overrides the name of the output file.
        change_imports (dict): Names of imported Bython modules, and their
                               Python alternatives.

    Returns:
        None
    """

    def convert_comments(code):
        """
        Converts C-style comments to Python-style comments.

        Args:
            code (str): The Bython code as a string

        Returns:
            str: Code with converted comments
        """
        code = re.sub(
            r"/\*(.*?)\*/", lambda m: f"'''{m.group(1)}'''", code, flags=re.DOTALL
        )
        code = re.sub(r"//(.*)", lambda m: f"#{m.group(1)}", code)
        return code

    filename = os.path.basename(filepath)
    output_filename = filename_prefix + _change_file_name(filename, outputname)

    with open(filepath, "r") as infile, open(output_filename, "w") as outfile:
        if add_true_line:
            outfile.write("true=True; false=False;\n")

        infile_str_raw = infile.read()
        infile_str_raw = add_pass_to_empty_blocks(infile_str_raw)
        infile_str_raw = convert_comments(infile_str_raw)

        indentation_level = 0
        indentation_sign = "    "
        infile_str_indented = ""

        # Fix indentation
        for line in infile_str_raw.splitlines():
            # Search for comments, and remove for now. Re-add them before writing to
            # result string
            m = re.search(r"[ \t]*(#.*$)", line)

            # Make sure # sign is not inside quotations. Delete match object if it is
            if m:
                m2 = re.search(r"[\"'].*#.*[\"']", m.group(0))
                if m2:
                    m = None

            add_comment = m.group(0) if m else ""

            # remove existing whitespace:
            line = line.lstrip()

            # skip empty lines:
            if not line:
                infile_str_indented += (
                    indentation_level * indentation_sign + add_comment.lstrip() + "\n"
                )
                continue

            (
                converted_line,
                is_function_def,
                is_empty_function,
            ) = convert_type_declaration(line)

            if not is_function_def:
                # Check for increased indentation
                if line.endswith("{"):
                    indented_line = (
                        indentation_sign * indentation_level + converted_line
                    )
                    indentation_level += 1
                # Check for reduced indent level
                elif line.startswith("}"):
                    indentation_level = max(0, indentation_level - 1)
                    indented_line = (
                        indentation_sign * indentation_level + converted_line
                    )
                # Add indentation
                else:
                    indented_line = (
                        indentation_sign * indentation_level + converted_line
                    )
            else:
                indented_line = converted_line
                if not is_empty_function:
                    indentation_level += 1

            # Replace { with : and remove }
            indented_line = re.sub(r"[\t ]*{[ \t]*", ":", indented_line)
            indented_line = re.sub(r"}[ \t]*", "", indented_line)
            indented_line = re.sub(r"\n:", ":", indented_line)

            infile_str_indented += indented_line + add_comment + "\n"

        # Support for extra, non-brace related stuff
        infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
        infile_str_indented = re.sub(r";\n", "\n", infile_str_indented)

        # Change imported names if necessary
        if change_imports:
            for module, alias in change_imports.items():
                infile_str_indented = re.sub(
                    r"(?<=import\s){}".format(module),
                    "{} as {}".format(alias, module),
                    infile_str_indented,
                )
                infile_str_indented = re.sub(
                    r"(?<=from\s){}(?=\s+import)".format(module),
                    alias,
                    infile_str_indented,
                )

        infile_str_indented = "from typing import Any\n\n" + infile_str_indented
        outfile.write(infile_str_indented)
