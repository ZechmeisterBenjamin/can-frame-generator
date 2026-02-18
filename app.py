from flask import Flask, render_template, request, jsonify
import os
import json
import re
from threading import Thread
import webbrowser

app = Flask(__name__, template_folder='.', static_folder='static')

# Configuration
CONFIG_FILE = "generator_config.json"
DEFAULT_CONFIG = {
    "path_cs": r"C:/Users/benja/Documents/htlwy/2526/ccit/CANSender/CANSender/Program.cs",
    "path_cpp": r"C:/Users/benja/Documents/htlwy/2526/ccit/14_COBS_Receive/05_CAN_Signals/UserCode/UserMain.cpp",
    "com_port": "COM3",
    "baud_rate": "1500000"
}

TYPE_MAPPING = {
    "int8_t / sbyte": ("int8_t", "sbyte"),
    "uint8_t / byte": ("uint8_t", "byte"),
    "int16_t / short": ("int16_t", "short"),
    "uint16_t / ushort": ("uint16_t", "ushort"),
    "int32_t / int": ("int32_t", "int"),
    "uint32_t / uint": ("uint32_t", "uint"),
    "int64_t / long": ("int64_t", "long"),
    "uint64_t / ulong": ("uint64_t", "ulong"),
    "float": ("float", "float"),
    "double": ("double", "double"),
    "bool": ("bool", "bool"),
}

# Global state
config = None
variables = []
state_machine = {
    "classname": "CanFrameSender",
    "states": [],
    "events": [],
    "transitions": []
}


def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return
        except:
            pass
    config = DEFAULT_CONFIG.copy()


def save_config():
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True, "Config saved"
    except Exception as e:
        return False, str(e)


def replace_in_file(file_path, start_tag, end_tag, new_content):
    if not os.path.exists(file_path):
        raise Exception(f"Path does not exist: {file_path}")

    content = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
                break
        except:
            continue
    
    if content is None:
        raise Exception(f"Cannot read file: {file_path}")

    pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
    
    if start_tag not in content:
        raise Exception(f"Tag not found: {start_tag}")

    match = re.search(f"^([ \t]*){re.escape(start_tag)}", content, re.MULTILINE)
    indent = match.group(1) if match else ""
    
    replacement = f"{start_tag}\n{indent}{new_content}\n{indent}{end_tag}"
    new_text = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    write_enc = 'utf-8-sig' if file_path.endswith(".cs") else 'utf-8'
    with open(file_path, 'w', encoding=write_enc) as f:
        f.write(new_text)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    global config
    data = request.json
    config.update(data)
    success, msg = save_config()
    return jsonify({"success": success, "message": msg})


@app.route('/api/variables', methods=['GET'])
def get_variables():
    return jsonify(variables)


@app.route('/api/variables', methods=['POST'])
def update_variables():
    global variables
    variables = request.json
    return jsonify({"success": True})


@app.route('/api/generate', methods=['POST'])
def generate_code():
    global variables
    data = request.json
    variables = data.get('variables', [])
    
    if not variables:
        return jsonify({"success": False, "message": "No variables defined"})

    final_vars = [(v['cpp'], v['cs'], v['name']) for v in variables if v['cpp'] and v['cs'] and v['name']]
    
    if not final_vars:
        return jsonify({"success": False, "message": "Invalid variables"})

    cs_struct = "public struct CanFrame {\n"
    cs_serialize = "    private static byte[] SerializeFrame(CanFrame frame) {\n        List<byte> bytes = new List<byte>();\n"
    for _, cs_type, name in final_vars:
        cs_struct += f"    public {cs_type} {name};\n"
        cs_serialize += f"        bytes.AddRange(BitConverter.GetBytes(frame.{name}));\n"
    cs_struct += "}"
    cs_serialize += "        return bytes.ToArray();\n    }"

    cpp_struct = "struct __attribute__((packed)) CanFrame {\n"
    for cpp_type, _, name in final_vars:
        cpp_struct += f"    {cpp_type} {name};\n"
    cpp_struct += "};"

    try:
        replace_in_file(config['path_cs'], "// [GENERATED_STRUCT_START]", "// [GENERATED_STRUCT_END]", cs_struct)
        replace_in_file(config['path_cs'], "// [GENERATED_SERIALIZE_START]", "// [GENERATED_SERIALIZE_END]", cs_serialize)
        replace_in_file(config['path_cpp'], "// [GENERATED_STRUCT_START]", "// [GENERATED_STRUCT_END]", cpp_struct)
        return jsonify({"success": True, "message": "Code generated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/state-machine', methods=['GET'])
def get_state_machine():
    return jsonify(state_machine)


@app.route('/api/state-machine', methods=['POST'])
def update_state_machine():
    global state_machine
    state_machine = request.json
    return jsonify({"success": True})


@app.route('/api/generate-sm', methods=['POST'])
def generate_state_machine():
    global state_machine
    data = request.json
    state_machine.update(data)
    
    classname = state_machine.get('classname', 'CanFrameSender').strip()
    states = [s.strip() for s in state_machine.get('states', []) if s.strip()]
    events = [e.strip() for e in state_machine.get('events', []) if e.strip()]
    transitions = state_machine.get('transitions', [])
    
    if not classname or not states or not events or not transitions:
        return jsonify({"success": False, "message": "Missing required fields"})

    states_enum = ", ".join(states)
    events_enum = ", ".join(events)

    code = f"""class {classname} {{
\tpublic:
\t\tenum class State {{ {states_enum} }} S;
\t\tenum class Event {{ None, {events_enum} }} E;
\t\t
\t\tbool\t\tiniOK = false;
\t\tuint64_t\tt_cyc = 0;
\t\tfloat\t\tt = 0;

\t\tbool\t\tclick_Edge = false;

\t\tvoid compute(float T)
\t\t{{
\t\t\t
\t\t\tif(!iniOK) t_cyc = 0;
\t\t\telse if(E == Event::None) t_cyc++;
\t\t\telse t_cyc = 0;
\t\t\tt = (t_cyc + 0.5f) * T;
\t\t\t
"""
    
    first_state = transitions[0][0] if transitions else states[0]
    code += f"\t\tif     (!iniOK) {{ E = Event::Init; S = State::{first_state}; }}\n"
    
    for trans in transitions:
        from_state, event, to_state, conditions, output_action = trans[:5]
        
        condition_parts = []
        for cond in conditions:
            var, op, val = cond
            if var == "click_Edge":
                condition_parts.append("click_Edge")
            else:
                condition_parts.append(f"{var} {op} {val}")
        
        condition_str = " && ".join(condition_parts)
        
        if condition_str:
            code += f"\t\telse if(S==State::{from_state} && {condition_str}) {{ E = Event::{event}; S = State::{to_state}; }}\n"
        else:
            code += f"\t\telse if(S==State::{from_state}) {{ E = Event::{event}; S = State::{to_state}; }}\n"
    
    code += "\t\telse{ E = Event::None; }\n\t\t\t\n\t\t\t//Outputs\n"
    
    output_actions = {}
    for trans in transitions:
        from_state, event, to_state, conditions, output_action = trans[:5]
        if output_action:
            output_actions[event] = output_action
    
    if output_actions:
        first_output = True
        for event in events:
            if event != "Init" and event in output_actions:
                action = output_actions[event]
                if first_output:
                    code += f"\t\tif\t\t\t(E==Event::{event:<20}\t) {action}\n"
                    first_output = False
                else:
                    code += f"\t\telse if\t(E==Event::{event:<20}\t) {action}\n"
        
        if not first_output:
            code += "\t\telse;\n"
    else:
        code += f"\t\tif\t\t\t(E==Event::Init) {{}}\n"
        code += "\t\t// TODO: Weitere Event-Outputs implementieren\n"
    
    code += "\t\t\n\t\tiniOK = true;\n\t\t}\n};"
    
    return jsonify({"success": True, "code": code})


@app.route('/api/type-mapping', methods=['GET'])
def get_type_mapping():
    return jsonify(TYPE_MAPPING)


if __name__ == '__main__':
    load_config()
    
    # Open browser automatically
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')
    
    Thread(target=open_browser, daemon=True).start()
    
    print("CAN Frame Generator running at http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000)
