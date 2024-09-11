import re
import os

def _ends_in_by(word):
    """
    Returns True if word ends in .by, else False

    Args:
        word (str): Filename to check

    Returns:
        bool: Whether the 'word' ends with '.by' or not
    """
    return word.endswith(".by")


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
    if outputname is not None:
        return outputname
    return name[:-3] + ".py" if _ends_in_by(name) else name + ".py"


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

    return [im + ".by" for im in imports + imports2]


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
        "def": "def"
    }
    return type_map.get(c_type, "Any")


def convert_variable_declaration(line):
    """
    Converts C-style variable declarations into Python variable annotations.

    Args:
        line (str): A line of code containing a variable declaration.

    Returns:
        str: The converted line in Python variable annotation format.
    """
    # Pattern to match variable declarations with initial values
    init_pattern = r"(\w+)\s+(\w+)\s*=\s*(.*?);"
    init_match = re.match(init_pattern, line)
    if init_match:
        var_type, var_name, value = init_match.groups()
        python_type = convert_c_type_to_python(var_type)
        return f"{var_name}: {python_type} = {value}"
    
    # Pattern to match variable declarations without initial values
    decl_pattern = r"(\w+)\s+(\w+)\s*;"
    decl_match = re.match(decl_pattern, line)
    if decl_match:
        var_type, var_name = decl_match.groups()
        python_type = convert_c_type_to_python(var_type)
        return f"{var_name}: {python_type} = None"
    
    return line


def convert_func_type_declaration(line):
    """
    Converts a C-style function signature into a Python function signature.
    Preserves Python-style function definitions without adding type hints.

    Args:
        line (str): A line of Bython code containing a function declaration

    Returns:
        tuple: A tuple containing the Python-style function definition, a boolean
               indicating whether it is a function definition, and another boolean
               indicating whether it is an empty function (no body).
    """
    # Check for Python-style function definition
    py_pattern = r"def\s+\w+\s*\(.*?\)\s*:$"
    py_match = re.match(py_pattern, line)
    if py_match:
        return f"{py_match.group(1)}:", True, False

    # Check for C-style function declaration
    c_pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*(\{)?\s*(\})?"
    c_match = re.match(c_pattern, line)
    if c_match:
        return_type, func_name, params, opening_brace, closing_brace = c_match.groups()
        params_converted = []
        for param in params.split(","):
            param = param.strip()
            if param:
                param_parts = param.split()
                param_type = " ".join(param_parts[:-1])
                param_name = param_parts[-1]
                python_type = convert_c_type_to_python(param_type)
                params_converted.append(f"{param_name}: {python_type}")
        
        return_hint = f" -> {convert_c_type_to_python(return_type)}" if return_type != "void" else ""

        is_empty_function = bool(opening_brace and closing_brace)

        if return_hint == " -> def":
            return (
                f"def {func_name}({', '.join(params_converted)}):",
                True,
                is_empty_function,
            )
        
        return (
            f"def {func_name}({', '.join(params_converted)}){return_hint}:",
            True,
            is_empty_function,
        )
    
    return line, False, False


def parse_line(line):
    indentation_level = 0

    # Remove indentation
    line = line.lstrip()

    # Convert C-style variable declarations
    line = convert_variable_declaration(line)

    # Convert C-style type declaration to Python type hint
    (
        converted_line,
        is_function_def,
        is_empty_function,
    ) = convert_func_type_declaration(line)

    # Fix indentation level
    if is_function_def:
        indented_line = converted_line
        if not is_empty_function:
            indentation_level += 1
    else:
        # Check for reduced indent level
        if line.startswith("}"):
            indentation_level = max(0, indentation_level - 1)
        # Check for increased indentation
        elif line.endswith("{"):
            line = line[:-1].rstrip() + ":"
            indentation_level += 1

    # Support for extra stuff
    line = re.sub(r"else\s+if", "elif", line)
    line = re.sub(r";\n", "\n", line)
    line = re.sub(r"(\S+)\s*&&\s*(\S+)", r"\1 and \2", line)
    line = re.sub(r"(\S+)\s*||\s*(\S+)", r"\1 or \2", line)
    line = re.sub(r'(?<!\!=)\s*!\s*([^\s\!=]+)', r'not \1', line)

    return line, indentation_level, is_empty_function


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

    filename = os.path.basename(filepath)
    output_filename = filename_prefix + _change_file_name(filename, outputname)

    with open(filepath, "r") as infile, open(output_filename, "w") as outfile:
        if add_true_line:
            outfile.write("true=True; false=False;\n")

        infile_str_raw = infile.read()
        infile_str_raw = convert_comments(infile_str_raw)

        indentation_level = 0
        indentation_sign = "    "
        infile_str_indented = ""

        in_single = 0
        in_double = 0

        for line in infile_str_raw.splitlines():

            # Check for comments or strings
            comment_start = []
            comment_end = []
            start = 0
            if in_single or in_double:
                comment_start.append(0)
            while True:
                if in_single:
                    single = line.find("'", start)
                    if single == -1:
                        break
                    else:
                        comment_end.append(single + 1)
                        start = single + 1
                        in_single = 0
                elif in_double:
                    double = line.find('"', start)
                    if double == -1:
                        break
                    else:
                        comment_end.append(double + 1)
                        start = double + 1
                        in_double = 0
                else:
                    py_comment = line.find("#", start)
                    c_comment = line.find("//", start)
                    single = line.find("'''", start)
                    double = line.find('"""', start)
                    if py_comment == -1 and c_comment == -1 and single == -1 and double == -1:
                        break
                    elif not (py_comment == -1 and c_comment == -1):
                        if py_comment == -1:
                            comment_start.append(c_comment)
                            comment_end.append(len(line))
                            line = line[0:c_comment] + "#" + line[c_comment + 2:]
                        elif c_comment == -1:
                            comment_start.append(py_comment)
                            comment_end.append(len(line))
                        elif py_comment > c_comment:
                            comment_start.append(c_comment)
                            comment_end.append(len(line))
                            line = line[0:c_comment] + "#" + line[c_comment + 2:]
                        else:
                            comment_start.append(py_comment)
                            comment_end.append(len(line))
                    elif single == -1:
                        in_double = 1
                        start = double + 1
                        comment_start.append(double)
                    elif double == -1:
                        in_single = 1
                        start = single + 1
                        comment_start.append(single)
                    elif single < double:
                        in_single = 1
                        start = single + 1
                        comment_start.append(single)
                    else:
                        in_double = 1
                        start = double + 1
                        comment_start.append(double)
            if len(comment_start) > len(comment_end):
                comment_end.append(len(line))

            indented_line = ""
            temp_indentation_level = 0
            for i in range(0, len(comment_start)):
                if comment_start[0] != 0:
                    str_carry, level_cary, is_empty_function = parse_first(line[0:comment_start[0]]
                    indented_line += str_carry
                    temp_indentation_level += level_carry
                indented_line += line[comment_start[i]:comment_end[i]]
                if i == len(comment_start) - 2 and comment_end[i] == len(line):
                    str_carry, level_cary = parse_last(line[comment_end[i]:comment_start[i+1]])
                    indented_line += str_carry
                    temp_indentation_level += level_carry
                elif i == len(comment_start) - 1 and comment_end[i] != len(line):
                    str_carry, level_cary = parse_last(line[comment_end[i]:len(line)])
                    indented_line += str_carry
                    temp_indentation_level += level_carry
                elif i == len(comment_start) - 1 and comment_end[i] == len(line):
                    pass
                else:
                    str_carry, level_cary = parse_line(line[comment_end[i]:comment_start[i+1]])
                    indented_line += str_carry
                    temp_indentation_level += level_carry

            indentation_level += temp_indentation_level

            # Add 'pass' for empty functions
            if is_empty_function:
                indented_line += "\n" + indentation_sign * (indentation_level + 1) + "pass"

            infile_str_indented += indentation_sign * indentation_level + indented_line + "\n"

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

        outfile.write(infile_str_indented)
