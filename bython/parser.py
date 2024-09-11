import re
import os

"""
This module provides functionality to convert Bython files to Python files.
It includes various helper functions for parsing and converting different
aspects of the code, such as imports, type declarations, and comments.
"""


def _change_file_name(name, outputname=None):
    """
    Modifies filenames to ensure they have a '.py' extension.

    If the filename ends with '.by', it replaces it with '.py'.
    If it doesn't end with '.by', it appends '.py'.

    Args:
        name (str): Original filename
        outputname (str, optional): Override for the output filename

    Returns:
        str: Modified filename with '.py' extension, or outputname if provided
    """
    if outputname is not None:
        return outputname
    return name[:-3] + ".py" if name.endswith(".by") else name + ".py"


def parse_imports(filename):
    """
    Extracts import statements from a file and returns a list of
    imported module names with '.by' appended.

    This function handles both 'import' and 'from ... import' statements.

    Args:
        filename (str): Path to the file to parse

    Returns:
        list of str: List of imported module names with '.by' appended
    """
    with open(filename, "r") as infile:
        infile_str = infile.read()

    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    return [im + ".by" for im in imports + imports2]


def type_template(name, map, containers_map):
    """
    Converts Bython types to their Python equivalents.

    This function handles both simple types and complex nested types.

    Args:
        name (str): The Bython type name to convert
        map (dict): Mapping of simple Bython types to Python types
        containers_map (dict): Mapping of container Bython types to Python types

    Returns:
        str: The equivalent Python type
    """
    if not name.startswith("by_"):
        return name
    elif name in map:
        return map[name]
    elif "<" in name[3:] or "[" in name[3:]:

        def parse_nested(type_str):
            if "<" not in type_str and "[" not in type_str:
                return map.get(type_str, type_str)

            outer, inner = (
                type_str.split("<", 1) if "<" in type_str else type_str.split("[", 1)
            )
            inner = inner.rstrip(">]")

            params = []
            depth = 0
            current = ""
            for char in inner:
                if char in "<[":
                    depth += 1
                elif char in ">]":
                    depth -= 1
                elif char == "," and depth == 0:
                    params.append(parse_nested(current.strip()))
                    current = ""
                    continue
                current += char
            if current:
                params.append(parse_nested(current.strip()))

            container = containers_map.get(outer, outer)
            return container[tuple(params) if len(params) > 1 else params[0]]

        return parse_nested(name[3:])
    else:
        return name[3:]


def convert_func_by_type_to_python(c_type):
    """
    Converts Bython function return types and parameter types to Python types.

    Args:
        c_type (str): Bython type to convert

    Returns:
        str: Equivalent Python type
    """
    type_map = {
        "by_def": "def",
        "by_void": "None",
        "by_bool": "bool",
        "by_int": "int",
        "by_long": "int",
        "by_float": "float",
        "by_double": "float",
        "by_char": "str",
        "by_str": "str",
        "by_string": "str",
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_short": "int",
        "by_byte": "int",
        "by_result": "Union",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_stack": "list",
        "by_optional": "Union[None, Any]",
    }
    containers_map = {
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_result": "Union",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_stack": "list",
    }
    return type_template(c_type, type_map, containers_map)


def convert_var_by_type_to_python(c_type):
    """
    Converts Bython variable types to Python types.

    Args:
        c_type (str): Bython type to convert

    Returns:
        str: Equivalent Python type
    """
    type_map = {
        "by_void": "Any",
        "by_bool": "bool",
        "by_int": "int",
        "by_long": "int",
        "by_float": "float",
        "by_double": "float",
        "by_char": "str",
        "by_str": "str",
        "by_string": "str",
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_short": "int",
        "by_byte": "int",
        "by_result": "Union",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_stack": "list",
        "by_optional": "Union[None, Any]",
    }
    containers_map = {
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_result": "Union",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_stack": "list",
    }
    return type_template(c_type, type_map, containers_map)


def convert_variable_declaration(line):
    """
    Converts Bython-style variable declarations to Python variable annotations.

    This function handles both declarations with and without initial values.

    Args:
        line (str): A line of code containing a variable declaration

    Returns:
        str: The converted line in Python variable annotation format
    """
    # Ignore return statements
    if line.strip().startswith("return"):
        return line

    # Pattern to match variable declarations with initial values
    init_pattern = r"(\w+)\s+(\w+)\s*=\s*(.*?)$"
    init_match = re.match(init_pattern, line)
    if init_match:
        var_type, var_name, value = init_match.groups()
        python_type = convert_var_by_type_to_python(var_type)
        return f"{var_name}: {python_type} = {value}"

    # Pattern to match variable declarations without initial values
    decl_pattern = r"(\w+)\s+(\w+)\s*$"
    decl_match = re.match(decl_pattern, line)
    if decl_match:
        var_type, var_name = decl_match.groups()
        python_type = convert_var_by_type_to_python(var_type)
        return f"{var_name}: {python_type} = None"

    return line


def parse_file(
    filepath, add_true_line, filename_prefix, outputname=None, change_imports=None
):
    """
    Converts a Bython file to a Python file and writes it to disk.

    This function handles the entire conversion process, including:
    - Adding support for C-style true/false
    - Converting comments
    - Converting function and variable declarations
    - Adjusting indentation
    - Handling imports

    Args:
        filepath (str): Path to the Bython file to parse
        add_true_line (bool): Whether to add support for C-style true/false
        filename_prefix (str): Prefix for the output filename
        outputname (str, optional): Override for the output filename
        change_imports (dict, optional): Mapping of imported Bython modules
                                         to their Python alternatives

    Returns:
        None
    """

    def convert_comments(code):
        """
        Converts C-style comments to Python-style comments.

        This function handles both multi-line and single-line comments.

        Args:
            code (str): The Bython code as a string

        Returns:
            str: Code with converted comments
        """
        # Convert multi-line comments
        code = re.sub(
            r"/\*(.*?)\*/",
            lambda m: f"'''\n{m.group(1).strip()}\n'''",
            code,
            flags=re.DOTALL,
        )
        # Convert single-line comments
        code = re.sub(r"//(.*)$", lambda m: f"#{m.group(1)}", code, flags=re.MULTILINE)
        return code

    def convert_func_type_declaration(line):
        """
        Converts Bython function declarations to Python function definitions.

        This function handles both C-style and Python-style function declarations.

        Args:
            line (str): A line of code containing a function declaration

        Returns:
            tuple: (converted_line, comment, is_function_def, is_empty_function)
                converted_line (str): The converted function definition
                comment (str): Any inline comment found after the declaration
                is_function_def (bool): Whether the line is a function definition
                is_empty_function (bool): Whether the function is empty (has no body)
        """
        # Check for Python-style function definition
        py_pattern = r"(def\s+\w+\s*\(.*?\)\s*:)(.*)$"
        py_match = re.match(py_pattern, line)
        if py_match:
            return py_match.group(1), py_match.group(2), True, False

        # Check for C-style function declaration
        c_pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*(\{)?\s*(\})?(.*)$"
        c_match = re.match(c_pattern, line)
        if c_match:
            (
                return_type,
                func_name,
                params,
                opening_brace,
                closing_brace,
                comment,
            ) = c_match.groups()
            params_converted = []
            for param in params.split(","):
                param = param.strip()
                if param:
                    param_parts = param.split()
                    if len(param_parts) > 1:
                        param_type = " ".join(param_parts[:-1])
                        param_name = param_parts[-1]
                        python_type = convert_func_by_type_to_python(param_type)
                        params_converted.append(f"{param_name}: {python_type}")
                    else:
                        params_converted.append(param)

            return_hint = f" -> {convert_func_by_type_to_python(return_type)}"
            is_empty_function = bool(closing_brace) or not opening_brace

            return (
                f"def {func_name}({', '.join(params_converted)}){return_hint}:",
                comment,
                True,
                is_empty_function,
            )

        return line, "", False, False

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
        inside_function = False
        multiline_comment = False

        for line in infile_str_raw.splitlines():
            stripped_line = line.strip()

            # Check for multiline comment start/end
            if stripped_line.startswith("'''") or stripped_line.endswith("'''"):
                multiline_comment = not multiline_comment
                infile_str_indented += (
                    indentation_sign * indentation_level + stripped_line + "\n"
                )
                continue

            # Preserve existing comments and multiline comment content
            if multiline_comment or stripped_line.startswith("#"):
                infile_str_indented += (
                    indentation_sign * indentation_level + stripped_line + "\n"
                )
                continue

            # skip empty lines:
            if not stripped_line:
                infile_str_indented += "\n"
                continue

            # Convert C-style type declaration to Python type hint
            (
                converted_line,
                comment,
                is_function_def,
                is_empty_function,
            ) = convert_func_type_declaration(stripped_line)

            # Convert variable declarations
            if not is_function_def:
                converted_line = convert_variable_declaration(converted_line)

            # Fix indentation level
            if is_function_def:
                if inside_function:
                    indentation_level -= 1
                inside_function = True
                indented_line = indentation_sign * indentation_level + converted_line
                indentation_level += 1
            else:
                # Check for increased indentation
                if stripped_line.endswith("{"):
                    indented_line = (
                        indentation_sign * indentation_level
                        + stripped_line[:-1].rstrip()
                        + ":"
                    )
                    indentation_level += 1
                # Check for reduced indent level
                elif stripped_line.startswith("}"):
                    indentation_level = max(0, indentation_level - 1)
                    inside_function = False
                    continue  # Skip this line as we don't need to write '}' in Python
                # Add indentation
                else:
                    indented_line = (
                        indentation_sign * indentation_level + converted_line
                    )

            # Add 'pass' for empty functions
            if is_empty_function:
                indented_line += "\n" + indentation_sign * indentation_level + "pass"
                inside_function = False
                indentation_level -= 1

            # Add comment if present
            if comment:
                indented_line += " " + comment

            infile_str_indented += indented_line + "\n"

        # Support for extra, non-brace related stuff
        infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
        infile_str_indented = re.sub(r";\n", "\n", infile_str_indented) 
        infile_str_indented = re.sub(r"(\S+)\s*&&\s*(\S+)", r"\1 and \2", infile_str_indented)
        infile_str_indented = re.sub(r"(\S+)\s*||\s*(\S+)", r"\1 or \2", infile_str_indented)
        infile_str_indented = re.sub(r'(?<!\!=)\s*!\s*([^\s\!=]+)', r'not \1', infile_str_indented)

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


"""
Additional module-level documentation:

This module provides a set of functions to convert Bython code to Python code. 
The main entry point is the `parse_file` function, which orchestrates the 
entire conversion process.

Key features:
1. Converts Bython-style variable and function declarations to Python syntax
2. Handles type conversions from Bython types to Python types
3. Converts C-style comments to Python comments
4. Manages indentation and braces-to-colon conversion
5. Supports import renaming

Usage:
    parse_file(filepath, add_true_line, filename_prefix, outputname, change_imports)

Where:
    - filepath: Path to the Bython file to be converted
    - add_true_line: Boolean to add 'true=True; false=False;' at the start of the file
    - filename_prefix: Prefix for the output Python file
    - outputname: (Optional) Override for the output filename
    - change_imports: (Optional) Dictionary to rename imported modules

The module uses regular expressions extensively for parsing and converting 
code. It also handles nested type declarations and converts them to appropriate 
Python type hints.
"""