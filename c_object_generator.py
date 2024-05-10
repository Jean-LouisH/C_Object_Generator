import os, os.path


project_namespace = ""
declspec_macro = ""
declspec_macro_header = ""
stdlib_malloc_substitute = ""
stdlib_free_substitute = ""
stdlib_substitute_header = ""
destination_directory = ""


def convert_to_snake_case(src_content):
    #Find areas to underscore
    token = ""
    parse_state = "is_reading_lower_characters"
    indices_to_underscore = []
    converted_src_content = ""

    for i in range(0, len(src_content), 1):
        character = src_content[i]
        if (character.isalnum()):
            token += character
            
            if i > 0:
                if (character.isupper() and parse_state == "is_reading_lower_characters"):
                    indices_to_underscore.append(i)
                    parse_state = "is_reading_upper_characters"
                elif (character.islower() and parse_state == "is_reading_upper_characters"):
                    parse_state = "is_reading_lower_characters"
            else:
                if character.isupper():
                    parse_state = "is_reading_upper_characters"
					
        converted_src_content += character

    #Insert the underscores
    indices_to_underscore.reverse()
    for i in indices_to_underscore:
        converted_src_content = converted_src_content[:i] + "_" + converted_src_content[i:]

    return converted_src_content


def generate_c_object(
            project_namespace,
            declspec_macro,
            declspec_macro_header,
            stdlib_malloc_substitute,
            stdlib_free_substitute,
            stdlib_substitute_header,
            c_object_name,
            destination_directory):

    snake_cass_project_namespace = convert_to_snake_case(project_namespace)  
    snake_case_object_name = convert_to_snake_case(c_object_name)
    project_object_name = project_namespace + c_object_name
    snake_case_project_object_name = convert_to_snake_case(project_object_name)
    include_guard_string = snake_case_project_object_name.upper() + "_H"
    new_class_filepath = destination_directory + "/" + snake_case_object_name.lower()

    #######################################
    #Header file
    #######################################
    header_contents = ""

    #include guard if
    header_contents += ("#ifndef " + include_guard_string + "\n" +
                        "#define " + include_guard_string + "\n\n"
                        )

    #declspec macro header
    if declspec_macro_header != "":
        header_contents += "#include <" + declspec_macro_header + ">\n\n"

    #extern C
    header_contents += "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n"

    #typedef struct
    header_contents += "typedef struct\n{\n}" + project_object_name + ";\n\n"


    #function definitions
    decl_spec_macro_insertion = ""
    
    if declspec_macro != "":
        decl_spec_macro_insertion = declspec_macro + " "

    project_class_allocation_string = project_object_name + "* " + snake_case_project_object_name.lower() + "_allocate()"
    project_class_free_string = "void " + snake_case_project_object_name.lower() + "_free(" + project_object_name + "* " + snake_case_object_name.lower() + ")"
    project_class_function_string = "void " + snake_case_project_object_name.lower() + "_function(" + project_object_name + "* " + snake_case_object_name.lower() + ")"

        
    header_contents += (decl_spec_macro_insertion + project_class_allocation_string + ";\n" +
                        decl_spec_macro_insertion + project_class_free_string + ";\n" +
                        decl_spec_macro_insertion + project_class_function_string + ";\n\n"
                        )

    #extern C endif
    header_contents += "#ifdef __cplusplus\n}\n#endif\n\n"
    
    #include guard endif
    header_contents += "#endif " + "/* " + include_guard_string + "*/\n"


    #Writing header file
    if not (os.path.exists(destination_directory)):
        os.mkdir(destination_directory)
        
    new_class_header_file = open(new_class_filepath + ".h", "w")
    new_class_header_file.write(header_contents)

    #######################################
    #Source file
    #######################################
    source_contents = ""

    #including headers
    source_contents += "#include " + "\"" + snake_case_object_name.lower() + ".h\"\n"
    source_contents += "#include " + "<stdlib.h>\n"


    #function implementations
    memory_allocation_function_name = stdlib_malloc_substitute
    memory_free_function_name = stdlib_free_substitute

    if stdlib_substitute_header == "":
        memory_allocation_function_name = "malloc"
        memory_free_function_name = "free"
    else:
        source_contents += "#include " + "<" + stdlib_substitute_header + ">\n"

    source_contents += "\n"

    source_contents += (project_class_allocation_string + "\n{\n" +
                        "\t" + project_object_name + "* " + snake_case_object_name.lower() + " = (" + project_object_name + "*) " + memory_allocation_function_name + "(sizeof(" + project_object_name + "));\n\n" +
                        "\tif (" + snake_case_object_name.lower() + " != NULL)\n" +
                        "\t{\n\t}\n\n\treturn " + snake_case_object_name.lower() + ";\n}\n\n" +

                        project_class_free_string + "\n{\n" +
                        "\tif (" + snake_case_object_name.lower() + " != NULL)\n" +
                        "\t{\n\t\t" + memory_free_function_name + "(" + snake_case_object_name.lower() + ");\n" +
                        "\t}\n}\n\n" +


                        project_class_function_string + "\n{\n" +
                        "\tif (" + snake_case_object_name.lower() + " != NULL)\n" +
                        "\t{\n\t}\n}\n\n"
                        )

    #Writing source file
    new_class_source_file = open(new_class_filepath + ".c", "w")
    new_class_source_file.write(source_contents)
    
    pass    


if __name__ == "__main__":
    input_string = input("\n\tC Object Generator\n\nEnter one or more Object names separated by commas -> ")
    tokens = input_string.split(", ")
    
    if project_namespace == "":
        project_namespace = input("\n\nEnter the project namespace to prepend to structs and functions -> ")

    define_declspec_decision = ''

    if declspec_macro != "" or declspec_macro_header != "":
        define_declspec_decision = 'n'
    else:
        input("\n\nDefine a declspec macro for functions? 'y' for yes, 'n' for no -> ")

    if define_declspec_decision == 'y':
        declspec_macro = input("\n\nEnter the declpec macro for functions -> ")
        declspec_macro_header = input("\nEnter the desclspec macros's destination directory relative to this script -> ")

    use_stdlib_decision = ''
    
    if stdlib_malloc_substitute != "" or stdlib_free_substitute != "" or stdlib_substitute_header != "":
        use_stdlib_decision = 'n'
    else:
        input("\n\nUse stdlib malloc and free? 'y' for yes, 'n' for no -> ")

    if use_stdlib_decision == 'y':
        stdlib_malloc_substitute = input("\n\nEnter the malloc substitution function name -> ")
        stdlib_free_substitute = input("\nEnter the free substitution function name -> ")
        stdlib_substitute_header = input("\nEnter the header include for stdlib substitution functions -> ")
        
    if destination_directory == "":
        destination_directory = input("\n\nEnter the destination directory relative to this script -> ")
        
    for token in tokens:
        generate_c_object(
            project_namespace,
            declspec_macro,
            declspec_macro_header,
            stdlib_malloc_substitute,
            stdlib_free_substitute,
            stdlib_substitute_header,
            token,
            destination_directory)

    print("...Done.\n")
