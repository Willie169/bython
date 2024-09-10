import re
import os

def _ends_in_by(word):
    return word.endswith(".by")

def _change_file_name(name, outputname=None):
    if outputname is not None:
        return outputname
    return name[:-3] + ".py" if _ends_in_by(name) else name + ".py"

def parse_imports(filename):
    with open(filename, "r") as infile:
        infile_str = infile.read()

    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    return [im + ".by" for im in imports + imports2]

def convert_func_c_type_to_python(c_type):
    type_map = {
        "int": "int",
        "float": "float",
        "double": "float",
        "complex": "complex",
        "char": "str",
        "string": "str",
        "void": "None",
        "bool": "bool",
        "tuple": "tuple",
        "set": "set",
        "def": "def"
    }
    return type_map.get(c_type, c_type)

def convert_var_c_type_to_python(c_type):
    type_map = {
        "int": "int",
        "float": "float",
        "double": "float",
        "complex": "complex",
        "char": "str",
        "string": "str",
        "void": "Any",
        "bool": "bool",
        "tuple": "tuple",
        "set": "set"
    }
    return type_map.get(c_type, c_type)

def convert_variable_declaration(line):
    # Pattern to match variable declarations with initial values
    init_pattern = r"(\w+)\s+(\w+)\s*=\s*(.*?)$"
    init_match = re.match(init_pattern, line)
    if init_match:
        var_type, var_name, value = init_match.groups()
        python_type = convert_var_c_type_to_python(var_type)
        return f"{var_name}: {python_type} = {value}"
    
    # Pattern to match variable declarations without initial values
    decl_pattern = r"(\w+)\s+(\w+)\s*$"
    decl_match = re.match(decl_pattern, line)
    if decl_match:
        var_type, var_name = decl_match.groups()
        python_type = convert_var_c_type_to_python(var_type)
        return f"{var_name}: {python_type} = None"
    
    return line

def convert_func_type_declaration(line):
    # Check for Python-style function definition
    py_pattern = r"(def\s+\w+\s*\(.*?\)\s*:)(.*)$"
    py_match = re.match(py_pattern, line)
    if py_match:
        return py_match.group(1), py_match.group(2), True, False

    # Check for C-style function declaration
    c_pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*(\{)?\s*(\})?(.*)$"
    c_match = re.match(c_pattern, line)
    if c_match:
        return_type, func_name, params, opening_brace, closing_brace, comment = c_match.groups()
        params_converted = []
        for param in params.split(","):
            param = param.strip()
            if param:
                param_parts = param.split()
                if len(param_parts) > 1:
                    param_type = " ".join(param_parts[:-1])
                    param_name = param_parts[-1]
                    python_type = convert_func_c_type_to_python(param_type)
                    params_converted.append(f"{param_name}: {python_type}")
                else:
                    params_converted.append(param)
        
        return_hint = f" -> {convert_func_c_type_to_python(return_type)}" if return_type != "void" else ""
        is_empty_function = bool(closing_brace)

        return (
            f"def {func_name}({', '.join(params_converted)}){return_hint}:",
            comment,
            True,
            is_empty_function,
        )
    
    return line, "", False, False

def parse_file(
    filepath, add_true_line, filename_prefix, outputname=None, change_imports=None
):
    def convert_comments(code):
        # Convert multi-line comments
        code = re.sub(
            r"/\*(.*?)\*/", lambda m: f"'''{m.group(1)}'''", code, flags=re.DOTALL
        )
        # Convert single-line comments
        code = re.sub(r"//(.*)$", lambda m: f"#{m.group(1)}", code, flags=re.MULTILINE)
        return code

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

        for line in infile_str_raw.splitlines():
            # Preserve existing comments
            comment_match = re.match(r"([ \t]*)(#.*$)", line)
            if comment_match:
                infile_str_indented += indentation_sign * indentation_level + comment_match.group(2) + "\n"
                continue

            # remove existing whitespace:
            line = line.strip()

            # skip empty lines:
            if not line:
                infile_str_indented += "\n"
                continue

            # Convert C-style type declaration to Python type hint
            converted_line, comment, is_function_def, is_empty_function = convert_func_type_declaration(line)

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
                if line.endswith("{"):
                    indented_line = indentation_sign * indentation_level + line[:-1].rstrip() + ":"
                    indentation_level += 1
                # Check for reduced indent level
                elif line.startswith("}"):
                    indentation_level = max(0, indentation_level - 1)
                    inside_function = False
                    continue  # Skip this line as we don't need to write '}' in Python
                # Add indentation
                else:
                    indented_line = indentation_sign * indentation_level + converted_line

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
