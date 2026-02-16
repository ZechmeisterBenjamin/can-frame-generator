import re
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

# --- PFADE (Mit r"..." und normalen Slashes für maximale Stabilität) ---
PATH_CS = r"C:/Users/benja/Documents/htlwy/2526/ccit/CANSender/CANSender/Program.cs"
PATH_CPP = r"C:/Users/benja/Documents/htlwy/2526/ccit/14_COBS_Receive/05_CAN_Signals/UserCode/UserMain.cpp"

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
        self.root.title("Variable Generator PRO - Drag & Sort")
        self.root.geometry("900x600")

        # Initialize paths
        self.path_cs = PATH_CS
        self.path_cpp = PATH_CPP

        self.rows = []

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

        self.setup_initial_data()

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
            self.setup_initial_data()

    def browse_cpp_file(self):
        file_path = filedialog.askopenfilename(
            title="C++ Datei auswählen",
            filetypes=[("C++ files", "*.cpp *.h *.hpp"), ("All files", "*.*")]
        )
        if file_path:
            self.path_cpp = file_path
            self.cpp_path_label.config(text=self.path_cpp)
            self.setup_initial_data()

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
        replacement = f"{start_tag}\n{new_content}\n{end_tag}"
        
        if start_tag not in content:
            raise Exception(f"Tag fehlt in {file_path}: {start_tag}")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorUI(root)
    root.mainloop()