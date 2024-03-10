import util

# EXAMPLE DATA_H GENERATOR
#
# # Generates the data.h file
# def generateDataHeader(data):
#     headers = ""
#     out = ""
#     # Generate initializers
#     for field in data.iter("struct"):
#         if "init" not in field.attrib:
#             continue
#         out += "int " + field.attrib["init"] + "(void);\n"

#     out += "\n"
#     # Generate data structures
#     for struct in data.iter("struct"):
#         if "comment" in struct.attrib:
#             out += util.generateComment(struct.attrib["comment"], 100)
#         out += "typedef struct " + struct.attrib["id"] + "_t {\n"

#         # Semaphores
#         out += "\tpthread_mutex_t " + struct.attrib["id"] + "Mutex;\n"

#         for field in struct:
#             if "comment" in field.attrib:
#                 out += util.generateComment(field.attrib["comment"], 100, "\t")
#             fieldId = (
#                 "*"
#                 if ("pointer" in field.attrib and field.attrib["pointer"] == "true")
#                 else ""
#             ) + field.attrib["id"]
#             if field.tag == "struct":
#                 out += "\tstruct " + field.attrib["id"] + "_t " + fieldId + ";\n"
#             elif field.tag == "field":
#                 fieldType = field.attrib["type"]
#                 # Deal with arrays
#                 if field.attrib["type"].endswith("]"):
#                     fieldId += "[" + field.attrib["type"].split("[")[1]
#                     fieldType = field.attrib["type"].split("[")[0]
#                 out += "\t" + fieldType + " " + fieldId + ";\n"

#                 # Create getter and setter headers
#                 headers += util.generateComment("Getter and setter for " + struct.attrib["id"] + "->" + field.attrib["id"], 100)
#                 fieldType = field.attrib["type"]
#                 isArray = False
#                 if "[" in field.attrib["type"]:
#                     fieldType = fieldType.split("[")[0]
#                     isArray = True
#                 headers += fieldType + " get" + util.capitalize(struct.attrib["id"]) + util.capitalize(field.attrib["id"]) + "();\n"
#                 headers += "void set" + util.capitalize(struct.attrib["id"]) + util.capitalize(field.attrib["id"]) + "(" + fieldType + " val);\n\n"

#                 headers += (
#                     fieldType
#                     + " "
#                     + util.getGetReference(struct, field)
#                     + "("
#                     + ("int index" if isArray else "")
#                     + ");\n"
#                 )
#                 headers += (
#                     "void "
#                     + util.getSetReference(struct, field)
#                     + "("
#                     + fieldType
#                     + " val"
#                     + (", int index" if isArray else "")
#                     + ");\n\n"
#                 )
#         out += "} " + struct.attrib["id"] + "_t;\n\n"
#     return out + "\n" + headers + "\n\n\n"


def dataFormat_h_generator(json_file):
    # define macros for readability
    DATA_TYPE_COL = 1
    SIGNAL_TYPE_COL = 5

    # output struct
    outputStruct = "typedef struct data_format {\n"
    # add header
    outputStruct += "  char header[5];   //<bsr>\n"
    # different types of signals so we can have comments denoting which type each section is
    outputStruct_mcc = "  // MCC Signals\n"
    outputStruct_hv = "  // HV Signals\n"
    outputStruct_main = "  // MainIO\n"
    outputStruct_mppt = "  // MPPT\n"
    outputStruct_bms = "  // BMS\n"
    outputStruct_software = "  // Software\n"
    getterSetterMethods = ""

    # open the data format json file and read it line by line
    # key is the name
    for key in json_file.keys():
        valueType = json_file[key][DATA_TYPE_COL]
        output = ""
        # if the type is uint8, use the correct types in c++
        if valueType == "uint8" or valueType == "uint16" or valueType == "uint64":
            output += "  " + valueType + "_t" + " " + key + ";\n"
            getterSetterMethods += valueType + "_t get_" + key + "();\n"
            getterSetterMethods += ("void set_" + key + "(" + valueType + "_t " + "val);\n\n")
        else:
            output += "  " + valueType + " " + key + ";\n"
            getterSetterMethods += valueType + " get_" + key + "();\n"
            getterSetterMethods += ("void set_" + key + "(" + valueType + " " + "val);\n\n")
        # put variable declaration in correct group
        if "MCC" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_mcc += output
        elif "High Voltage" in json_file[key][SIGNAL_TYPE_COL] or "Battery;Supplemental" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_hv += output
        elif "Main IO" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_main += output
        elif "Solar Array" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_mppt += output
        elif "Battery" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_bms += output
        elif "Software" in json_file[key][SIGNAL_TYPE_COL]:
            outputStruct_software += output
        # not part of any group
        else:
            outputStruct += output

    # add all groups to outputStruct
    outputStruct += f"{outputStruct_mcc}\n{outputStruct_hv}\n{outputStruct_main}\n{outputStruct_mppt}\n{outputStruct_bms}\n{outputStruct_software}\n"
    # footer
    outputStruct += "  char footer[6];   //</bsr>\n"
    # add the closing brace
    outputStruct += "} data_format;\n\n"
    # add the two struct instances
    outputStruct += "// Data storage structs\nextern data_format dfwrite;\nextern data_format dfdata;\n\n"

    return f"\n{outputStruct}\n{getterSetterMethods}"


def dataFormat_cpp_generator(json_file):
    # define macros for readability
    DATA_TYPE_COL = 1

    mutexes = ""
    getterSetterMethods = ""
    # add a short preface to set the pack power by multiplying pack voltage and current.
    copyStructMethod = "void copyDataStructToWriteStruct() {\n  dfwrite_mutex.lock();\n" 
    copyStructMethod += f'  char[6] header = "<bsr>";\n  char[7] footer = "</bsr>";\n  for (int i = 0; i < 5; i++) dfwrite.header[i] = header[i]; \n'

    # open the data format json file and read it line by line
    # key is the name
    for key in json_file.keys():
        valueType = json_file[key][DATA_TYPE_COL]
        mutexName = key + "_mutex"
        # create a mutex for the variable
        mutexes += "Mutex " + mutexName + ";\n"
        # add to the copy struct method
        copyStructMethod += "  dfwrite." + key + " = get_" + key + "();\n"
        # if the type is uint, use the correct types in c++
        if valueType == "uint8" or valueType == "uint16" or valueType == "uint64":
            getterSetterMethods += f"{valueType}_t get_{key}() {{\n  {mutexName}.lock();\n  {valueType}_t val = dfdata.{key};\n" + \
                                    f"  {mutexName}.unlock();\n  return val;\n}}\n"

            getterSetterMethods += f"void set_{key}({valueType}_t val) {{\n  {mutexName}.lock();\n  dfdata.{key} = val;\n" + \
                                    f"  {mutexName}.unlock();\n}}\n\n"

        else:
            getterSetterMethods += f"{valueType} get_{key}() {{\n  {mutexName}.lock();\n  {valueType} val = dfdata.{key};\n" + \
                                    f"  {mutexName}.unlock();\n  return val;\n}}\n"
            getterSetterMethods += f"void set_{key}({valueType} val) {{\n  {mutexName}.lock();\n  dfdata.{key} = val;\n" + \
                                    f"  {mutexName}.unlock();\n}}\n\n"
    # set footer
    copyStructMethod += "  for (int i = 0; i < 6; i++) dfwrite.footer[i] = footer[i];\n"
    # add closing brace to copy struct method
    copyStructMethod += "  dfwrite_mutex.unlock();\n}\n"

    return f"\n{copyStructMethod}\n{mutexes}\n{getterSetterMethods}"

def sofi_h_generator(json_file):
    DATA_TYPE_COL = 1
    outputStruct = "typedef struct sofi_struct {\n"
    getterSetterMethods = ""

    for key in json_file.keys():
        valueType = json_file[key][DATA_TYPE_COL]
        # if the type is uint8 and uint16, use the correct types in c++
        if valueType == "uint8" or valueType == "uint16" or valueType == "uint64":
            outputStruct += "  " + valueType + "_t" + " " + key + ";\n"
            getterSetterMethods += valueType + "_t get_" + key + "();\n"
            getterSetterMethods += ("void set_" + key + "(" + valueType + "_t " + "val);\n\n")
        else:
            outputStruct += "  " + valueType + " " + key + ";\n"
            getterSetterMethods += valueType + " get_" + key + "();\n"
            getterSetterMethods += ("void set_" + key + "(" + valueType + " " + "val);\n\n")


    outputStruct += "} sofi_struct;\n\n"
    outputStruct += "// Data storage structs\nextern sofi_struct sofi_data;\n"

    return f"{outputStruct}\n{getterSetterMethods}"


def sofi_cpp_generator(json_file):
    DATA_TYPE_COL = 1

    mutexes = ""
    getterSetterMethods = ""

    for key in json_file.keys():
        valueType = json_file[key][DATA_TYPE_COL]
        mutexName = key + "_mutex"
        # create a mutex for the variable
        mutexes += "Mutex " + mutexName + ";\n"
        # if the type is uint, use the correct types in c++
        if valueType == "uint8" or valueType == "uint16" or valueType == "uint64":
            getterSetterMethods += f"{valueType}_t get_{key}() {{\n  {mutexName}.lock();\n  {valueType}_t val = dfdata.{key};\n" + \
                                    f"  {mutexName}.unlock();\n  return val;\n}}\n"

            getterSetterMethods += f"void set_{key}({valueType}_t val) {{\n  {mutexName}.lock();\n  dfdata.{key} = val;\n" + \
                                    f"  {mutexName}.unlock();\n}}\n\n"

        else:
            getterSetterMethods += f"{valueType} get_{key}() {{\n  {mutexName}.lock();\n  {valueType} val = dfdata.{key};\n" + \
                                    f"  {mutexName}.unlock();\n  return val;\n}}\n"
            getterSetterMethods += f"void set_{key}({valueType} val) {{\n  {mutexName}.lock();\n  dfdata.{key} = val;\n" + \
                                    f"  {mutexName}.unlock();\n}}\n\n"


    return f"{mutexes}\n{getterSetterMethods}"