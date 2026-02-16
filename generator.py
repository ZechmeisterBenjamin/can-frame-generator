import re
import os
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

# --- KONFIGURATIONSDATEI ---
CONFIG_FILE = "generator_config.json"

# --- DEFAULT PFADE ---
DEFAULT_CONFIG = {
    "path_cs": r"C:/Users/benja/Documents/htlwy/2526/ccit/CANSender/CANSender/Program.cs",
    "path_cpp": r"C:/Users/benja/Documents/htlwy/2526/ccit/14_COBS_Receive/05_CAN_Signals/UserCode/UserMain.cpp",
    "com_port": "COM3",
    "baud_rate": "1500000"
}

# Datatype mapping
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

class GeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN Frame & State Machine Generator")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)

        # Konfiguration laden
        self.config = self.load_config()
        
        self.path_cs = self.config["path_cs"]
        self.path_cpp = self.config["path_cpp"]
        self.com_port = self.config["com_port"]
        self.baud_rate = self.config["baud_rate"]

        self.rows = []
        self.states = []
        self.events = []
        self.transitions = []

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Configuration Tab
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Konfiguration")
        self.setup_config_tab()

        # Variables Tab
        self.variables_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.variables_tab, text="Variablen")
        self.setup_variables_tab()

        # State Machine Tab
        self.statemachine_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.statemachine_tab, text="Zustandsautomaten")
        self.setup_statemachine_tab()

        self.setup_initial_data()
    
    def load_config(self):
        """Konfiguration aus Datei laden oder Standard verwenden"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Konfiguration in Datei speichern"""
        config = {
            "path_cs": self.path_cs,
            "path_cpp": self.path_cpp,
            "com_port": self.com_port,
            "baud_rate": self.baud_rate
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Fehler", f"Konfiguration konnte nicht gespeichert werden: {e}")

    def setup_config_tab(self):
        path_frame = tk.LabelFrame(self.config_tab, text="Dateipfade", padx=10, pady=10)
        path_frame.pack(fill="x", padx=10, pady=5)

        # C# Path
        cs_frame = tk.Frame(path_frame)
        cs_frame.pack(fill="x", pady=5)
        tk.Label(cs_frame, text="C# Datei:", width=12, anchor="w").pack(side="left")
        self.cs_path_label = tk.Label(cs_frame, text=self.path_cs, fg="blue", anchor="w")
        self.cs_path_label.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(cs_frame, text="Durchsuchen", command=self.browse_cs_file).pack(side="right")

        # C++ Path
        cpp_frame = tk.Frame(path_frame)
        cpp_frame.pack(fill="x", pady=5)
        tk.Label(cpp_frame, text="C++ Datei:", width=12, anchor="w").pack(side="left")
        self.cpp_path_label = tk.Label(cpp_frame, text=self.path_cpp, fg="blue", anchor="w")
        self.cpp_path_label.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(cpp_frame, text="Durchsuchen", command=self.browse_cpp_file).pack(side="right")

        # C# Settings Frame
        settings_frame = tk.LabelFrame(self.config_tab, text="C# Projekteinstellungen", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # COM Port
        com_frame = tk.Frame(settings_frame)
        com_frame.pack(fill="x", pady=5)
        tk.Label(com_frame, text="COM-Port:", width=12, anchor="w").pack(side="left")
        self.com_port_entry = tk.Entry(com_frame, width=20)
        self.com_port_entry.insert(0, self.com_port)
        self.com_port_entry.pack(side="left", padx=5)
        tk.Button(com_frame, text="Speichern", command=self.save_com_port).pack(side="left")

        # Baud Rate
        baud_frame = tk.Frame(settings_frame)
        baud_frame.pack(fill="x", pady=5)
        tk.Label(baud_frame, text="Baudrate:", width=12, anchor="w").pack(side="left")
        self.baud_rate_entry = tk.Entry(baud_frame, width=20)
        self.baud_rate_entry.insert(0, self.baud_rate)
        self.baud_rate_entry.pack(side="left", padx=5)
        tk.Button(baud_frame, text="Speichern", command=self.save_baud_rate).pack(side="left")

    def setup_variables_tab(self):
        # Header
        header_frame = tk.Frame(self.variables_tab)
        header_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(header_frame, text="Sort", width=10).pack(side="left")
        tk.Label(header_frame, text="Datentyp", width=20, anchor="w").pack(side="left")
        tk.Label(header_frame, text="C++ Typ", width=15, anchor="w").pack(side="left")
        tk.Label(header_frame, text="C# Typ", width=15, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Variablenname", width=20, anchor="w").pack(side="left")

        # Container für die Zeilen
        self.main_frame = tk.Frame(self.variables_tab)
        self.main_frame.pack(fill="both", expand=True, padx=10)

        # Buttons unten
        btn_frame = tk.Frame(self.variables_tab, pady=10)
        btn_frame.pack(fill="x", padx=10)
        
        tk.Button(btn_frame, text="+ Variable hinzufügen", command=self.add_row, bg="#e1e1e1", padx=10).pack(side="left")
        tk.Button(btn_frame, text="CODE GENERIEREN", command=self.generate, bg="green", fg="white", font=('Arial', 10, 'bold'), padx=20).pack(side="right")

    def browse_cs_file(self):
        file_path = filedialog.askopenfilename(
            title="C# Datei auswählen",
            filetypes=[("C# files", "*.cs"), ("All files", "*.*")]
        )
        if file_path:
            self.path_cs = file_path
            self.cs_path_label.config(text=self.path_cs)
            self.save_config()
            self.setup_initial_data()

    def browse_cpp_file(self):
        file_path = filedialog.askopenfilename(
            title="C++ Datei auswählen",
            filetypes=[("C++ files", "*.cpp *.h *.hpp"), ("All files", "*.*")]
        )
        if file_path:
            self.path_cpp = file_path
            self.cpp_path_label.config(text=self.path_cpp)
            self.save_config()
            self.setup_initial_data()

    def save_com_port(self):
        """COM-Port speichern und C# Code aktualisieren"""
        self.com_port = self.com_port_entry.get().strip()
        if self.com_port:
            self.save_config()
            try:
                self.update_cs_port_and_baud()
                messagebox.showinfo("Erfolg", f"COM-Port '{self.com_port}' gespeichert und C# Code aktualisiert")
            except Exception as e:
                messagebox.showerror("Fehler", f"COM-Port gespeichert, aber C# Code konnte nicht aktualisiert werden:\n{e}")
        else:
            messagebox.showerror("Fehler", "COM-Port darf nicht leer sein")

    def save_baud_rate(self):
        """Baudrate speichern und C# Code aktualisieren"""
        baud = self.baud_rate_entry.get().strip()
        if baud.isdigit():
            self.baud_rate = baud
            self.save_config()
            try:
                self.update_cs_port_and_baud()
                messagebox.showinfo("Erfolg", f"Baudrate '{self.baud_rate}' gespeichert und C# Code aktualisiert")
            except Exception as e:
                messagebox.showerror("Fehler", f"Baudrate gespeichert, aber C# Code konnte nicht aktualisiert werden:\n{e}")
        else:
            messagebox.showerror("Fehler", "Baudrate muss eine Zahl sein")

    def update_cs_port_and_baud(self):
        """Aktualisiert COM-Port und Baudrate in der C# Datei"""
        self.replace_in_file(
            self.path_cs,
            "// [PORTNAME_START]",
            "// [PORTNAME_END]",
            'private const string PortName = "' + self.com_port + '";'
        )
        self.replace_in_file(
            self.path_cs,
            "// [BAUDRATE_START]",
            "// [BAUDRATE_END]",
            'private const int BaudRate = ' + self.baud_rate + ';'
        )

    def setup_initial_data(self):
        # Clear existing rows
        for row in self.rows:
            row["frame"].destroy()
        self.rows.clear()
        
        initial_vars = self.read_variables_from_files()
        for cpp, cs, name in initial_vars:
            self.add_row(cpp, cs, name)

    def read_variables_from_files(self):
        try:
            # Read C# file
            cs_vars = {}
            try:
                with open(self.path_cs, 'r', encoding='utf-8-sig') as f:
                    cs_content = f.read()
                    start_idx = cs_content.find("// [GENERATED_STRUCT_START]")
                    end_idx = cs_content.find("// [GENERATED_STRUCT_END]")
                    if start_idx != -1 and end_idx != -1:
                        struct_content = cs_content[start_idx:end_idx]
                        # Extract: public TYPE NAME;
                        for match in re.finditer(r'public\s+(\w+)\s+(\w+);', struct_content):
                            cs_type, name = match.groups()
                            cs_vars[name] = cs_type
            except:
                pass
            
            # Read C++ file
            cpp_vars = {}
            try:
                with open(self.path_cpp, 'r', encoding='utf-8') as f:
                    cpp_content = f.read()
                    start_idx = cpp_content.find("// [GENERATED_STRUCT_START]")
                    end_idx = cpp_content.find("// [GENERATED_STRUCT_END]")
                    if start_idx != -1 and end_idx != -1:
                        struct_content = cpp_content[start_idx:end_idx]
                        # Extract: TYPE NAME;
                        for match in re.finditer(r'(\w+[\s\*]*)\s+(\w+);', struct_content):
                            cpp_type, name = match.groups()
                            cpp_vars[name] = cpp_type.strip()
            except:
                pass
            
            # Combine both
            result = []
            seen_names = set()
            for name in cpp_vars:
                if name in cs_vars:
                    result.append((cpp_vars[name], cs_vars[name], name))
                    seen_names.add(name)
            
            return result if result else []
        except:
            return []

    def add_row(self, cpp="", cs="", name=""):
        row_frame = tk.Frame(self.main_frame)
        row_frame.pack(fill="x", pady=2)

        # Sortier-Buttons
        up_btn = tk.Button(row_frame, text="▲", width=2, command=lambda: self.move_up(row_frame))
        up_btn.pack(side="left", padx=1)
        down_btn = tk.Button(row_frame, text="▼", width=2, command=lambda: self.move_down(row_frame))
        down_btn.pack(side="left", padx=1)

        # Dropdown für Datentypen
        type_combo = ttk.Combobox(row_frame, width=18, state="readonly")
        type_combo['values'] = list(TYPE_MAPPING.keys())
        type_combo.pack(side="left", padx=5)

        cpp_ent = tk.Entry(row_frame, width=15)
        cpp_ent.insert(0, cpp)
        cpp_ent.pack(side="left", padx=5)

        cs_ent = tk.Entry(row_frame, width=15)
        cs_ent.insert(0, cs)
        cs_ent.pack(side="left", padx=5)

        name_ent = tk.Entry(row_frame, width=25)
        name_ent.insert(0, name)
        name_ent.pack(side="left", padx=5)

        btn_del = tk.Button(row_frame, text="X", fg="red", command=lambda: self.delete_row(row_frame))
        btn_del.pack(side="right")

        # Bind dropdown selection to fill C++ and C# types
        def on_type_select(event):
            selected = type_combo.get()
            if selected in TYPE_MAPPING:
                cpp_type, cs_type = TYPE_MAPPING[selected]
                cpp_ent.delete(0, tk.END)
                cpp_ent.insert(0, cpp_type)
                cs_ent.delete(0, tk.END)
                cs_ent.insert(0, cs_type)

        type_combo.bind("<<ComboboxSelected>>", on_type_select)

        self.rows.append({"frame": row_frame, "cpp": cpp_ent, "cs": cs_ent, "name": name_ent})

    def move_up(self, frame):
        idx = self.get_index(frame)
        if idx > 0:
            self.rows[idx], self.rows[idx-1] = self.rows[idx-1], self.rows[idx]
            self.refresh_ui()

    def move_down(self, frame):
        idx = self.get_index(frame)
        if idx < len(self.rows) - 1:
            self.rows[idx], self.rows[idx+1] = self.rows[idx+1], self.rows[idx]
            self.refresh_ui()

    def get_index(self, frame):
        for i, row in enumerate(self.rows):
            if row["frame"] == frame: return i
        return -1

    def refresh_ui(self):
        for row in self.rows:
            row["frame"].pack_forget()
        for row in self.rows:
            row["frame"].pack(fill="x", pady=2)

    def delete_row(self, frame):
        idx = self.get_index(frame)
        if idx != -1:
            self.rows[idx]["frame"].destroy()
            self.rows.pop(idx)

    def replace_in_file(self, file_path, start_tag, end_tag, new_content):
        if not os.path.exists(file_path):
            raise Exception(f"Pfad existiert nicht: {file_path}")

        content = None
        for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                    break
            except Exception:
                continue
        
        if content is None:
            raise Exception(f"Lesezugriff verweigert: {file_path}")

        pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
        
        if start_tag not in content:
            raise Exception(f"Tag fehlt in {file_path}: {start_tag}")

        # Finde die Einrückung der Start-Tag Zeile
        match = re.search(f"^([ \t]*){re.escape(start_tag)}", content, re.MULTILINE)
        indent = match.group(1) if match else ""
        
        replacement = f"{start_tag}\n{indent}{new_content}\n{indent}{end_tag}"
        new_text = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        write_enc = 'utf-8-sig' if file_path.endswith(".cs") else 'utf-8'
        with open(file_path, 'w', encoding=write_enc) as f:
            f.write(new_text)

    def generate(self):
        final_vars = []
        for row in self.rows:
            cpp = row["cpp"].get().strip()
            cs = row["cs"].get().strip()
            name = row["name"].get().strip()
            if cpp and cs and name:
                final_vars.append((cpp, cs, name))

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
            self.replace_in_file(self.path_cs, "// [GENERATED_STRUCT_START]", "// [GENERATED_STRUCT_END]", cs_struct)
            self.replace_in_file(self.path_cs, "// [GENERATED_SERIALIZE_START]", "// [GENERATED_SERIALIZE_END]", cs_serialize)
            self.replace_in_file(self.path_cpp, "// [GENERATED_STRUCT_START]", "// [GENERATED_STRUCT_END]", cpp_struct)
            messagebox.showinfo("Erfolg", "Code erfolgreich generiert!")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def setup_statemachine_tab(self):
        """Tab für Zustandsautomaten mit responsivem Design"""
        main_container = tk.Frame(self.statemachine_tab)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Konfigurierungs-Bereich (oben)
        config_frame = tk.LabelFrame(main_container, text="Konfiguration", padx=10, pady=10)
        config_frame.pack(fill="x", pady=(0, 5))

        # Klassenname
        class_frame = tk.Frame(config_frame)
        class_frame.pack(fill="x", pady=(0, 5))
        tk.Label(class_frame, text="Klassenname:", width=15, anchor="w").pack(side="left")
        self.classname_entry = tk.Entry(class_frame, width=40)
        self.classname_entry.insert(0, "CanFrameSender")
        self.classname_entry.pack(side="left", padx=5, fill="x", expand=True)

        # States und Events nebeneinander
        input_container = tk.Frame(config_frame)
        input_container.pack(fill="both", expand=True, pady=(0, 5))

        # States
        states_frame = tk.LabelFrame(input_container, text="States", padx=5, pady=5)
        states_frame.pack(side="left", fill="both", expand=True, padx=(0, 2))
        self.states_text = tk.Text(states_frame, height=4, width=25)
        self.states_text.pack(fill="both", expand=True)
        self.states_text.bind("<KeyRelease>", lambda e: self.update_transition_combos())

        # Events
        events_frame = tk.LabelFrame(input_container, text="Events", padx=5, pady=5)
        events_frame.pack(side="left", fill="both", expand=True, padx=2)
        self.events_text = tk.Text(events_frame, height=4, width=25)
        self.events_text.pack(fill="both", expand=True)
        self.events_text.bind("<KeyRelease>", lambda e: self.update_transition_combos())

        # Mittlerer Bereich: Übergänge Builder + Liste (nebeneinander)
        middle_container = tk.Frame(main_container)
        middle_container.pack(fill="both", expand=True, pady=5)

        # Linke Seite: Builder
        builder_frame = tk.LabelFrame(middle_container, text="Neuer Übergang", padx=8, pady=8)
        builder_frame.pack(side="left", fill="both", expand=False, padx=(0, 5), ipadx=5)

        # Von State
        tk.Label(builder_frame, text="Von State:", font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.trans_from_combo = ttk.Combobox(builder_frame, width=20, state="readonly")
        self.trans_from_combo.pack(fill="x", pady=(0, 5))

        # Event
        tk.Label(builder_frame, text="Event:", font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.trans_event_combo = ttk.Combobox(builder_frame, width=20, state="readonly")
        self.trans_event_combo.pack(fill="x", pady=(0, 5))

        # Zu State
        tk.Label(builder_frame, text="Zu State:", font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.trans_to_combo = ttk.Combobox(builder_frame, width=20, state="readonly")
        self.trans_to_combo.pack(fill="x", pady=(0, 5))

        # Bedingungen
        tk.Label(builder_frame, text="Bedingungen (optional):", font=("Arial", 8, "bold")).pack(anchor="w", pady=(5, 2))

        # Time Condition (t)
        time_frame = tk.Frame(builder_frame)
        time_frame.pack(fill="x", pady=(0, 5))
        self.time_check = tk.BooleanVar(value=False)
        tk.Checkbutton(time_frame, text="Zeit (t)", variable=self.time_check, width=8).pack(side="left")
        self.time_op_combo = ttk.Combobox(time_frame, width=3, state="readonly", values=[">", "<", "==", ">=", "<=", "!="])
        self.time_op_combo.set(">")
        self.time_op_combo.pack(side="left", padx=(0, 3))
        self.time_val_entry = tk.Entry(time_frame, width=8)
        self.time_val_entry.insert(0, "0")
        self.time_val_entry.pack(side="left")

        # Click Edge Condition
        click_frame = tk.Frame(builder_frame)
        click_frame.pack(fill="x", pady=(0, 8))
        self.click_check = tk.BooleanVar(value=False)
        tk.Checkbutton(click_frame, text="Click Edge (wahr)", variable=self.click_check, width=18).pack(anchor="w")

        # Add Button
        add_trans_btn = tk.Button(builder_frame, text="✓ Übergang hinzufügen", command=self.add_transition, bg="#90EE90", font=("Arial", 9, "bold"))
        add_trans_btn.pack(fill="x")

        # Rechte Seite: Übergänge Liste
        list_frame = tk.LabelFrame(middle_container, text="Definierte Übergänge", padx=8, pady=8)
        list_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Listbox mit Scrollbar
        scrollbar_trans = tk.Scrollbar(list_frame)
        scrollbar_trans.pack(side="right", fill="y")
        
        self.transitions_listbox = tk.Listbox(list_frame, height=10, yscrollcommand=scrollbar_trans.set, font=("Courier", 8))
        self.transitions_listbox.pack(fill="both", expand=True)
        scrollbar_trans.config(command=self.transitions_listbox.yview)

        # Delete Button
        del_trans_btn = tk.Button(list_frame, text="✗ Markierten Übergang löschen", command=self.delete_transition, bg="#FFB6C6")
        del_trans_btn.pack(fill="x", pady=(5, 0))

        # Move Buttons Frame
        move_frame = tk.Frame(list_frame)
        move_frame.pack(fill="x", pady=(5, 0))
        tk.Button(move_frame, text="↑ Nach oben", command=self.move_transition_up, width=12).pack(side="left", padx=2)
        tk.Button(move_frame, text="↓ Nach unten", command=self.move_transition_down, width=12).pack(side="left", padx=2)
        tk.Button(move_frame, text="✎ Bearbeiten", command=self.edit_transition, bg="#FFE4B5", width=12).pack(side="left", padx=2)

        # Unterer Bereich: Code Output + Buttons
        bottom_container = tk.Frame(main_container)
        bottom_container.pack(fill="both", expand=True, pady=(5, 0))

        # Code Output
        right_frame = tk.LabelFrame(bottom_container, text="Generierter C++ Code", padx=10, pady=10)
        right_frame.pack(fill="both", expand=True, side="top")

        # Code Text mit Scrollbar
        scrollbar = tk.Scrollbar(right_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.code_output = tk.Text(right_frame, height=10, yscrollcommand=scrollbar.set, font=("Courier", 8))
        self.code_output.pack(fill="both", expand=True)
        scrollbar.config(command=self.code_output.yview)

        # Buttons Bereich
        btn_frame = tk.Frame(bottom_container)
        btn_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        tk.Button(btn_frame, text="CODE GENERIEREN", command=self.generate_statemachine, bg="green", fg="white", font=('Arial', 10, 'bold')).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Code kopieren", command=self.copy_code_to_clipboard, font=('Arial', 9)).pack(side="right", padx=2)
        tk.Button(btn_frame, text="Beispiel laden", command=self.load_example_sm, font=('Arial', 9)).pack(side="right", padx=2)

        # State machine transitions storage
        self.sm_transitions = []

    def load_example_sm(self):
        """Lädt ein Beispiel für einen Zustandsautomaten"""
        self.classname_entry.delete(0, tk.END)
        self.classname_entry.insert(0, "CanFrameSender")

        self.states_text.delete(1.0, tk.END)
        self.states_text.insert(1.0, "Ready\npauseFirstFrame\npauseSecondFrame\npauseThirdFrame")
        
        self.events_text.delete(1.0, tk.END)
        self.events_text.insert(1.0, "Init\nsendFirstFrame\nsendSecondFrame\nsendThirdFrame\nsendFourthFrame")
        
        # Übergänge mit neuer Struktur (conditions als Liste)
        # Format: (from_state, event, to_state, conditions, is_wildcard)
        self.sm_transitions = [
            ("Ready", "sendFirstFrame", "pauseFirstFrame", [("click_Edge", "", "")], False),
            ("pauseFirstFrame", "sendSecondFrame", "pauseSecondFrame", [("t", ">", "0.3")], False),
            ("pauseSecondFrame", "sendThirdFrame", "pauseThirdFrame", [("t", ">", "1.0")], False),
            ("pauseThirdFrame", "sendFourthFrame", "Ready", [("t", ">", "1.9")], False)
        ]
        self.refresh_transitions_listbox()
        self.update_transition_combos()

    def generate_statemachine(self):
        """Generiert den C++ Code für den Zustandsautomaten"""
        classname = self.classname_entry.get().strip()
        if not classname:
            messagebox.showerror("Fehler", "Klassenname ist erforderlich!")
            return

        states_raw = self.states_text.get(1.0, tk.END).strip()
        events_raw = self.events_text.get(1.0, tk.END).strip()

        if not states_raw or not events_raw:
            messagebox.showerror("Fehler", "States und Events sind erforderlich!")
            return

        if not self.sm_transitions:
            messagebox.showerror("Fehler", "Mindestens ein Übergang ist erforderlich!")
            return

        states = [s.strip() for s in states_raw.split('\n') if s.strip()]
        events = [e.strip() for e in events_raw.split('\n') if e.strip()]

        # Generiere C++ Code
        cpp_code = self._generate_cpp_statemachine(classname, states, events, self.sm_transitions)
        
        self.code_output.delete(1.0, tk.END)
        self.code_output.insert(1.0, cpp_code)

    def _generate_cpp_statemachine(self, classname, states, events, transitions):
        """Generiert C++ Zustandsautomaten Code"""
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
        # Erstes Transition als Init
        first_state = transitions[0][0] if transitions else states[0]
        code += f"\t\tif     (!iniOK) {{ E = Event::Init; S = State::{first_state}; }}\n"
        
        # Weitere Übergänge
        for trans in transitions:
            # Handle both old format (4 elements) and new format (5 elements with wildcard marker)
            if len(trans) == 5:
                from_state, event, to_state, conditions, is_wildcard = trans
            else:
                from_state, event, to_state, conditions = trans
                is_wildcard = False
            
            condition_str = ""
            
            if conditions:
                cond_parts = []
                for var, op, val in conditions:
                    if var == "click_Edge":
                        cond_parts.append("click_Edge")
                    else:
                        cond_parts.append(f"{var} {op} {val}")
                condition_str = " && ".join(cond_parts)
            
            if condition_str:
                code += f"\t\telse if(S==State::{from_state} && {condition_str}) {{ E = Event::{event}; S = State::{to_state}; }}\n"
            else:
                code += f"\t\telse if(S==State::{from_state}) {{ E = Event::{event}; S = State::{to_state}; }}\n"
        
        code += """\t\telse{ E = Event::None; }
\t\t\t
\t\t\t//Outputs
\t\t\tif\t\t\t(E==Event::Init) {}
\t\t\t// TODO: Weitere Event-Outputs implementieren
\t\t\t
\t\t\tiniOK = true;
\t\t}
}};"""

        return code

    def update_transition_combos(self):
        """Aktualisiert die Dropdowns mit aktuellen States und Events"""
        states_raw = self.states_text.get(1.0, tk.END).strip()
        events_raw = self.events_text.get(1.0, tk.END).strip()
        
        states = [s.strip() for s in states_raw.split('\n') if s.strip()]
        events = [e.strip() for e in events_raw.split('\n') if e.strip()]
        
        # Füge "(alle)" Option hinzu
        states_with_all = ["(alle)"] + states
        
        self.trans_from_combo['values'] = states_with_all
        self.trans_to_combo['values'] = states
        self.trans_event_combo['values'] = events

    def add_transition(self):
        """Fügt einen neuen Übergang hinzu"""
        from_state = self.trans_from_combo.get()
        event = self.trans_event_combo.get()
        to_state = self.trans_to_combo.get()
        
        if not from_state or not event or not to_state:
            messagebox.showerror("Fehler", "Bitte State, Event und Zielstate auswählen!")
            return
        
        # Bedingungen bauen
        conditions = []
        
        # Time-Bedingung
        if self.time_check.get():
            time_op = self.time_op_combo.get()
            time_val = self.time_val_entry.get().strip()
            if not time_val:
                messagebox.showerror("Fehler", "Zeitwert erforderlich!")
                return
            conditions.append(("t", time_op, time_val))
        
        # Click Edge Bedingung (immer nur "true")
        if self.click_check.get():
            conditions.append(("click_Edge", "", ""))
        
        # Wildcard-Handling: "(alle)" expandieren
        if from_state == "(alle)":
            states_raw = self.states_text.get(1.0, tk.END).strip()
            states = [s.strip() for s in states_raw.split('\n') if s.strip()]
            for state in states:
                self.sm_transitions.append((state, event, to_state, conditions, True))  # True = wildcard marker
        else:
            self.sm_transitions.append((from_state, event, to_state, conditions, False))
        
        self.refresh_transitions_listbox()
        self.reset_transition_form()

    def delete_transition(self):
        """Löscht den markierten Übergang"""
        selection = self.transitions_listbox.curselection()
        if selection:
            idx = selection[0]
            self.sm_transitions.pop(idx)
            self.refresh_transitions_listbox()
        else:
            messagebox.showwarning("Info", "Bitte einen Übergang auswählen!")

    def move_transition_up(self):
        """Verschiebt den markierten Übergang nach oben"""
        selection = self.transitions_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx > 0:
                self.sm_transitions[idx], self.sm_transitions[idx-1] = self.sm_transitions[idx-1], self.sm_transitions[idx]
                self.refresh_transitions_listbox()
                self.transitions_listbox.selection_set(idx-1)
        else:
            messagebox.showwarning("Info", "Bitte einen Übergang auswählen!")

    def move_transition_down(self):
        """Verschiebt den markierten Übergang nach unten"""
        selection = self.transitions_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.sm_transitions) - 1:
                self.sm_transitions[idx], self.sm_transitions[idx+1] = self.sm_transitions[idx+1], self.sm_transitions[idx]
                self.refresh_transitions_listbox()
                self.transitions_listbox.selection_set(idx+1)
        else:
            messagebox.showwarning("Info", "Bitte einen Übergang auswählen!")

    def edit_transition(self):
        """Lädt den markierten Übergang zum Bearbeiten in die Felder"""
        selection = self.transitions_listbox.curselection()
        if selection:
            idx = selection[0]
            trans = self.sm_transitions[idx]
            
            # Handle both old format (4 elements) and new format (5 elements with wildcard marker)
            if len(trans) == 5:
                from_state, event, to_state, conditions, is_wildcard = trans
            else:
                from_state, event, to_state, conditions = trans
                is_wildcard = False
            
            # Fülle die Felder
            self.trans_from_combo.set(from_state)
            self.trans_event_combo.set(event)
            self.trans_to_combo.set(to_state)
            
            # Bedingungen laden
            self.time_check.set(False)
            self.click_check.set(False)
            
            for var, op, val in conditions:
                if var == "click_Edge":
                    self.click_check.set(True)
                elif var == "t":
                    self.time_check.set(True)
                    self.time_op_combo.set(op)
                    self.time_val_entry.delete(0, tk.END)
                    self.time_val_entry.insert(0, val)
            
            # Entferne den alten Übergang (wird als neuer hinzugefügt)
            self.sm_transitions.pop(idx)
            self.refresh_transitions_listbox()
            
            messagebox.showinfo("Info", "Übergang geladen! Bearbeite und klicke 'Übergang hinzufügen'")
        else:
            messagebox.showwarning("Info", "Bitte einen Übergang auswählen!")

    def refresh_transitions_listbox(self):
        """Aktualisiert die Listbox mit Übergängen"""
        self.transitions_listbox.delete(0, tk.END)
        for trans in self.sm_transitions:
            if len(trans) == 5:
                from_state, event, to_state, conditions, is_wildcard = trans
            else:
                from_state, event, to_state, conditions = trans
                is_wildcard = False
            
            wildcard_marker = " [*]" if is_wildcard else ""
            
            if conditions:
                cond_strs = []
                for cond in conditions:
                    var, op, val = cond
                    if var == "click_Edge":
                        cond_strs.append("click_Edge")
                    else:
                        cond_strs.append(f"{var} {op} {val}")
                cond_text = " && ".join(cond_strs)
                text = f"{from_state}{wildcard_marker} → [{event}] → {to_state}  WENN  {cond_text}"
            else:
                text = f"{from_state}{wildcard_marker} → [{event}] → {to_state}"
            self.transitions_listbox.insert(tk.END, text)

    def reset_transition_form(self):
        """Setzt das Übergangs-Eingabe-Formular zurück"""
        self.trans_from_combo.set("")
        self.trans_event_combo.set("")
        self.trans_to_combo.set("")
        self.time_check.set(False)
        self.click_check.set(False)
        self.time_op_combo.set(">")
        self.time_val_entry.delete(0, tk.END)
        self.time_val_entry.insert(0, "0")

    def copy_code_to_clipboard(self):
        """Kopiert den generierten Code in die Zwischenablage"""
        code = self.code_output.get(1.0, tk.END)
        if code.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Erfolg", "Code wurde in die Zwischenablage kopiert!")
        else:
            messagebox.showerror("Fehler", "Kein Code zum Kopieren vorhanden!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorUI(root)
    root.mainloop()