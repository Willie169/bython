import re
import os

"""
This module provides functionality to convert Bython files to Python files.
It includes various helper functions for parsing and converting different
aspects of the code, such as imports, type declarations, and comments.
"""


def _change_file_name(name, outputname=None):
    """
    Changes *.by filenames to *.py filenames. If filename does not end in .by, 
    it adds .py to the end.

    Args:
        name (str):         Filename to edit
        outputname (str):   Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.py at the end (unless 'outputname' is
        specified, then that is returned).
    """

    # If outputname is specified, return that
    if outputname is not None:
        return outputname

    # Otherwise, create a new name
    if name.endswith(".by"):
        return name[:-3] + ".py"

    else:
        return name + ".py"


def parse_imports(filename):
    """
    Reads the file, and scans for imports. Returns all the assumed filename
    of all the imported modules (ie, module name appended with ".by")

    Args:
        filename (str):     Path to file

    Returns:
        list of str: All imported modules, suffixed with '.by'. Ie, the name
        the imported files must have if they are bython files.
    """
    infile = open(filename, 'r')
    infile_str = ""

    for line in infile:
        infile_str += line


    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    imports_with_suffixes = [im + ".by" for im in imports + imports2]

    return imports_with_suffixes


def type_template(name, sole_map, type_map, containers_map):
    """
    Converts Bython types to their Python equivalents.

    This function handles both simple types and complex nested types,
    including Union types created with the '|' operator.

    Args:
        name (str): The Bython type name to convert
        sole_map (dict): Mapping of simple Bython types to Python types
        type_map (dict): Mapping of Bython types to Python types
        containers_map (dict): Mapping of container Bython types to Python types

    Returns:
        str: The equivalent Python type
    """
    def parse_nested(type_str):
        if type_str in sole_map:
            return sole_map[type_str]
        if type_str in type_map:
            return type_map[type_str]
        
        if "<" not in type_str and "[" not in type_str:
            return type_str

        container, content = type_str.split("[", 1) if "[" in type_str else type_str.split("<", 1)
        content = content.rstrip("]>")

        parsed_container = containers_map.get(container, container)

        params = []
        depth = 0
        current = ""
        for char in content:
            if char in "<[":
                depth += 1
            elif char in ">]":
                depth -= 1
            elif char == "," and depth == 0:
                params.append(parse_union(current.strip()))
                current = ""
                continue
            current += char
        if current:
            params.append(parse_union(current.strip()))

        return f"{parsed_container}[{', '.join(params)}]"

    def parse_union(type_str):
        if "|" not in type_str:
            return parse_nested(type_str)
        
        union_types = [parse_nested(t.strip()) for t in type_str.split("|")]
        if len(union_types) > 1:
            return f"Union[{', '.join(union_types)}]"
        return union_types[0]

    return parse_nested(name)


def convert_func_type(by_type):
    """
    Converts Bython function return types types to Python types.

    Args:
        c_type (str): Bython type to convert

    Returns:
        str: Equivalent Python type
    """
    sole_map = {
        "by_def": "def",
        "by_py": "Optional[Any]"
    }
    type_map = {
        "by_def": "Optional[Any]",
        "by_void": "None",
        "by_Any": "Any",
        "by_bool": "bool",
        "by_int": "int",
        "by_short": "int",
        "by_byte": "int",
        "by_long": "int",
        "by_float": "float",
        "by_double": "float",
        "by_char": "str",
        "by_str": "str",
        "by_string": "str",
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_dict": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_stack": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue"
    }
    containers_map = {
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_dict": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_stack": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_union": "Union",
        "by_result": "Union",
        "by_optional": "Optional"
    }
    return type_template(by_type, sole_map, type_map, containers_map)


def convert_var_type(by_type):
    """
    Converts Bython variable types and parameter type to Python types.

    Args:
        c_type (str): Bython type to convert

    Returns:
        str: Equivalent Python type
    """
    sole_map = {
        "by_py": "Optional[Any]"
    }
    type_map = {
        "by_void": "Optional[Any]",
        "by_Any": "Any",
        "by_bool": "bool",
        "by_int": "int",
        "by_short": "int",
        "by_byte": "int",
        "by_long": "int",
        "by_float": "float",
        "by_double": "float",
        "by_char": "str",
        "by_str": "str",
        "by_string": "str",
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_dict": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_stack": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue"
    }
    containers_map = {
        "by_map": "dict",
        "by_unordered_map": "dict",
        "by_dict": "dict",
        "by_vector": "list",
        "by_array": "list",
        "by_list": "list",
        "by_array_list": "list",
        "by_linked_list": "list",
        "by_stack": "list",
        "by_tuple": "tuple",
        "by_set": "set",
        "by_unordered_set": "set",
        "by_deque": "collections.deque",
        "by_priority_queue": "queue.PriorityQueue",
        "by_queue": "queue.Queue",
        "by_union": "Union",
        "by_result": "Union",
        "by_optional": "Optional"
    }
    return type_template(by_type, sole_map, type_map, containers_map)


def parse_file(filepath, add_true_line, filename_prefix, outputname=None, change_imports=None):
    """
    Converts a bython file to a python file and writes it to disk.

    Args:
        filename (str):             Path to the bython file you want to parse.
        add_true_line (boolean):    Whether to add a line at the top of the
                                    file, adding support for C-style true/false
                                    in addition to capitalized True/False.
        filename_prefix (str):      Prefix to resulting file name (if -c or -k
                                    is not present, then the files are prefixed
                                    with a '.').
        outputname (str):           Optional. Override name of output file. If
                                    omitted it defaults to substituting '.by' to
                                    '.py'    
        change_imports (dict):      Names of imported bython modules, and their 
                                    python alternative.
    """
    filename = os.path.basename(filepath)
    filedir = os.path.dirname(filepath)

    infile = open(filepath, 'r')
    outfile = open(filename_prefix + _change_file_name(filename, outputname), 'w')

    indentation_level = 0
    indentation_sign = "    "

    if add_true_line:
        outfile.write("true=True; false=False;\n")

    # Read file to string
    infile_str_raw = ""
    for line in infile:
        infile_str_raw += line

    # Add 'pass' where there is only a {}. 
    # 
    # DEPRECATED FOR NOW. This way of doing
    # it is causing a lot of problems with {} in comments. The feature is removed
    # until I find another way to do it. 
    
    # infile_str_raw = re.sub(r"{[\s\n\r]*}", "{\npass\n}", infile_str_raw)

    # Fix indentation
    infile_str_indented = ""
    for line in infile_str_raw.split("\n"):
        # Search for comments, and remove for now. Re-add them before writing to
        # result string
        m = re.search(r"[ \t]*(#.*$)", line)

        # Make sure # sign is not inside quotations. Delete match object if it is
        if m is not None:
            m2 = re.search(r"[\"'].*#.*[\"']", m.group(0))
            if m2 is not None:
                m = None

        if m is not None:
            add_comment = m.group(0)
            line = re.sub(r"[ \t]*(#.*$)", "", line)
        else:
            add_comment = ""

        # skip empty lines:
        if line.strip() in ('\n', '\r\n', ''):
            infile_str_indented += indentation_level*indentation_sign + add_comment.lstrip() + "\n"
            continue

        # remove existing whitespace:
        line = line.lstrip()
        
        # Check for reduced indent level
        for i in list(line):
            if i == "}":
                indentation_level -= 1

        # Add indentation
        for i in range(indentation_level):
            line = indentation_sign + line

        # Check for increased indentation
        for i in list(line):
            if i == "{":
                indentation_level += 1

        # Replace { with : and remove }
        line = re.sub(r"[\t ]*{[ \t]*", ":", line)
        line = re.sub(r"}[ \t]*", "", line)
        line = re.sub(r"\n:", ":", line)

        infile_str_indented += line + add_comment + "\n"


    # Support for extra, non-brace related stuff
    infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
    infile_str_indented = re.sub(r";\n", "\n", infile_str_indented) 
    infile_str_indented = re.sub(r"(\S+)\s+\&\&\s+(\S+)", r"\1 and \2", infile_str_indented)
    infile_str_indented = re.sub(r"(\S+)\s+\|\|\s+(\S+)", r"\1 or \2", infile_str_indented)
    infile_str_indented = re.sub(r'(?<!\!=)\s*!\s*([^\s\!=]+)', r'not \1', infile_str_indented)

    # Change imported names if necessary
    if change_imports is not None:
        for module in change_imports:
            infile_str_indented = re.sub("(?<=import\\s){}".format(module), "{} as {}".format(change_imports[module], module), infile_str_indented)
            infile_str_indented = re.sub("(?<=from\\s){}(?=\\s+import)".format(module), change_imports[module], infile_str_indented)

    outfile.write(infile_str_indented)

    infile.close()
    outfile.close()

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