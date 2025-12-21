import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import random
import re
import os 
import importlib.util 
import sys 

class IPPInterface:
    def __init__(self, root, base_dir):
        self.root = root
        self.root.title("RPG Pad Pro Parser")
        
        self.root.state('zoomed') 

        self.COLOR_ODD = "#FFFFFF"
        self.COLOR_EVEN = "#EFEFEF"
        self.base_dir = base_dir 
        self.RULESET_DIR = os.path.join(base_dir, "Rules") 
        self.ruleset_funcs = {} 

        # --- State for Table Parsing ---
        self.in_table = False
        self.cell_content_start_index = None

        # --- Menu Bar (File I/O) ---
        self.create_menu()

        # --- Layout Containers ---
        main_container = tk.Frame(root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_container, padx=10, width=150)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = tk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Left Widgets (Editor) ---
        tk.Label(left_frame, text="Script Editor", font=("Arial", 11, "bold")).pack(anchor="w")
        self.input_text = tk.Text(left_frame, width=40, height=30, wrap=tk.WORD, undo=True, bg="#F0F0F0")
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # INPUT STRIPING CONFIGURATION 
        self.input_text.tag_configure("even_line", background="#DDDDDD")
        self.input_text.bind("<KeyRelease>", lambda e: self.apply_shading(self.input_text))
        self.input_text.bind("<ButtonRelease>", lambda e: self.apply_shading(self.input_text))

        # --- Center Widgets (Controls) ---
        tk.Label(control_frame, text="Active Ruleset:", font=("Arial", 9)).pack(pady=(20, 5))
        self.package_selector = ttk.Combobox(control_frame, state="readonly", width=18)
        self.package_selector.pack(pady=5)
        
        self.refresh_btn = tk.Button(control_frame, text="Load Rulesets", command=self.refresh_ruleset_list)
        self.refresh_btn.pack(pady=5)
        self.package_selector.bind("<<ComboboxSelected>>", self._load_active_ruleset) 
        
        tk.Label(control_frame, text="Start Table:", font=("Arial", 9)).pack(pady=(20, 5))
        self.table_selector = ttk.Combobox(control_frame, state="readonly", width=18)
        self.table_selector.pack(pady=5)
        
        tk.Label(control_frame, text="Run X Times:", font=("Arial", 9)).pack(pady=(20, 5))
        self.run_count_entry = tk.Entry(control_frame, width=8, justify='center')
        self.run_count_entry.insert(0, "5")
        self.run_count_entry.pack(pady=5)

        self.generate_btn = tk.Button(control_frame, text="Generate >>", command=self.run_generation, height=2, bg="#dddddd", font=("Arial", 10, "bold"))
        self.generate_btn.pack(pady=30)

        self.clear_btn = tk.Button(control_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.BOTTOM, pady=20)

        # --- Right Widgets (Output) ---
        tk.Label(right_frame, text="Rich Output", font=("Arial", 11, "bold")).pack(anchor="w")
        self.output_text = tk.Text(right_frame, width=40, height=30, wrap=tk.WORD, bg=self.COLOR_ODD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.setup_output_tags() 

        # --- Initial Setup ---
        self._ensure_rules_directory() 
        self.load_sample_script()
        self.refresh_ruleset_list()
        self._load_active_ruleset()
        self.apply_shading(self.input_text)
        
    # --- FILE SYSTEM & LOADING LOGIC ---
    def _ensure_rules_directory(self):
        try:
            os.makedirs(self.RULESET_DIR, exist_ok=True)
        except OSError as e:
            messagebox.showerror("File System Error", f"Could not create ruleset directory '{self.RULESET_DIR}': {e}")
            
    def refresh_ruleset_list(self):
        ruleset_names = []
        try:
            for entry in os.scandir(self.RULESET_DIR):
                if entry.is_dir():
                    ruleset_names.append(entry.name)
        except FileNotFoundError:
            self._ensure_rules_directory()
            return

        current_selection = self.package_selector.get()
        
        if not ruleset_names:
            self.package_selector['values'] = ["-- No Rulesets Found --"]
            self.package_selector.set("-- No Rulesets Found --")
        else:
            self.package_selector['values'] = ruleset_names
            if current_selection in ruleset_names:
                self.package_selector.set(current_selection)
            elif "Core" in ruleset_names: 
                 self.package_selector.set("Core")
            else:
                self.package_selector.current(0)
                
    def _load_module_from_path(self, file_path, module_name):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None: return None
        module = importlib.util.module_from_spec(spec)
        sys.path.append(os.path.dirname(file_path)) 
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            messagebox.showerror("Ruleset Error", f"Error loading rule file '{file_path}': {e}")
            return None
        finally:
            sys.path.pop() 
            
    def _load_active_ruleset(self, event=None):
        ruleset_name = self.package_selector.get()
        if ruleset_name.startswith("--"):
             self.ruleset_funcs = {}
             return
             
        ruleset_path = os.path.join(self.RULESET_DIR, ruleset_name)
        new_funcs = {}
        errors = []
        
        for item in os.listdir(ruleset_path):
            file_path = os.path.join(ruleset_path, item)
            
            if os.path.isfile(file_path) and (item.endswith('.py') or item.endswith('.rule')):
                module_name = item.split('.')[0]
                module = self._load_module_from_path(file_path, module_name)
                
                if module:
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if callable(attr) and not attr_name.startswith("__"):
                            new_funcs[attr_name] = attr 
                else:
                    errors.append(item)

        self.ruleset_funcs = new_funcs
        
        # Check for essential CORE ENGINE functions 
        CORE_ENGINE_FUNCS = ['parse_tables', 'roll_on_table', 'resolve_table_tags', 'math_evaluator', 'case_converter', 'list_sorter'] 
        if not all(func in self.ruleset_funcs for func in CORE_ENGINE_FUNCS):
            messagebox.showerror("Ruleset Error", f"The ruleset '{ruleset_name}' is missing one or more CORE ENGINE functions: {', '.join(CORE_ENGINE_FUNCS)}. Ensure necessary files are present.")
            self.ruleset_funcs = {}
            
        self.refresh_table_list()


    # --- Generation Logic ---
    def refresh_table_list(self):
        if 'parse_tables' not in self.ruleset_funcs:
            self.table_selector['values'] = ["-- Ruleset Not Loaded --"]
            self.table_selector.set("-- Ruleset Not Loaded --")
            return

        script = self.input_text.get("1.0", tk.END)
        tables = self.ruleset_funcs['parse_tables'](script) 
        
        table_names = list(tables.keys())
        self.table_selector['values'] = table_names
        
        if table_names:
            if self.table_selector.get() not in table_names:
                self.table_selector.current(0)
        else:
            self.table_selector.set("")

    def run_generation(self):
        CORE_ENGINE_FUNCS = ['parse_tables', 'roll_on_table', 'resolve_table_tags', 'math_evaluator', 'case_converter', 'list_sorter']
        if not all(func in self.ruleset_funcs for func in CORE_ENGINE_FUNCS):
            messagebox.showerror("Execution Error", "Core Ruleset is not fully loaded. Check for errors during load.")
            return

        parse_tables_func = self.ruleset_funcs['parse_tables']
        roll_on_table_func = self.ruleset_funcs['roll_on_table']
        resolve_table_tags_func = self.ruleset_funcs['resolve_table_tags']

        script = self.input_text.get("1.0", tk.END)
        tables = parse_tables_func(script)

        if not tables:
            messagebox.showinfo("Info", "No tables found in script.")
            return

        try:
            num_runs = int(self.run_count_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for 'Run X Times'.")
            return

        start_table = self.table_selector.get()
        if not start_table or start_table not in tables:
            if tables:
                start_table = list(tables.keys())[0]
            else:
                return

        self.output_text.delete("1.0", tk.END)
        
        # --- INITIALIZE VARIABLES & HELPERS ---
        self.ruleset_funcs['variables'] = {}
        
        # NEW: Pass the UI update function so the engine can keep the window alive
        self.ruleset_funcs['gui_update'] = self.root.update

        for i in range(num_runs):
            base_text = roll_on_table_func(start_table, tables) 
            
            # --- Resolve Tags (now includes robust deck pick resolution) ---
            final_text = resolve_table_tags_func(base_text, tables, self.ruleset_funcs) 
            
            # --- Resolve \a modifier ---
            final_text = self.resolve_a_an_modifier(final_text)

            self.parse_and_insert_html(final_text)

            if i < num_runs - 1:
                self.output_text.insert(tk.END, "═" * 40, "separator")
                self.output_text.insert(tk.END, "\n")
                
    # --- A/An Modifier Resolver ---
    def resolve_a_an_modifier(self, text):
        """
        Replaces the '\a' modifier with 'a' or 'an' based on the following word, 
        skipping any intervening spaces or HTML tags.
        """
        VOWELS = "AEIOUaeiou"

        def final_substitute(match):
            # Find the position right after the '\a' tag
            index = match.end()
            text_after_a = match.string[index:]
            
            # Find the true start of the next word/text, skipping spaces and HTML tags
            i = 0
            while i < len(text_after_a):
                char = text_after_a[i]
                
                if char.isspace():
                    i += 1
                    continue
                    
                if char == '<':
                    # Skip entire HTML tag
                    tag_end = text_after_a.find('>', i)
                    if tag_end != -1:
                        i = tag_end + 1
                        continue
                    else:
                        i += 1 # Malformed tag, continue
                        continue
                
                # Found the start of the next significant word/character
                first_char = char
                break
                
                i += 1
            else:
                # Reached end of string
                first_char = ''

            # Determine replacement
            if first_char and first_char in VOWELS:
                return "an"
            else:
                return "a"

        # Use re.sub to find all instances of \a
        text = re.sub(r'\\a', final_substitute, text)
        return text

    # --- UI & Helper Methods ---
                
    def setup_output_tags(self):
        """Defines the visual styles for the HTML tags for the output window, including table styles."""
        base_font = "Arial"
        
        # Base Text Tags
        self.output_text.tag_configure("bold", font=(base_font, 10, "bold"))
        self.output_text.tag_configure("italic", font=(base_font, 10, "italic"))
        self.output_text.tag_configure("underline", underline=True)
        self.output_text.tag_configure("h1", font=(base_font, 24, "bold"), spacing3=10)
        self.output_text.tag_configure("h2", font=(base_font, 16, "bold"), spacing3=5)
        self.output_text.tag_configure("h3", font=(base_font, 12, "bold"))
        self.output_text.tag_configure("red", foreground="red")
        self.output_text.tag_configure("blue", foreground="blue")
        self.output_text.tag_configure("green", foreground="green")
        self.output_text.tag_configure("gray", foreground="gray")
        self.output_text.tag_configure("separator", foreground="#888888", justify='center', spacing1=10, spacing3=10)
        
        # --- Table Tags ---
        self.output_text.tag_configure("table_border", 
                                       lmargin1=10, 
                                       lmargin2=10,
                                       rmargin=10,  
                                       background="#F9F9F9") 
        
        # The 'td_cell' tag defines the appearance of each cell
        self.output_text.tag_configure("td_cell", 
                                       borderwidth=1, 
                                       relief=tk.RIDGE, 
                                       font=(base_font, 10), 
                                       lmargin1=5, 
                                       lmargin2=5,
                                       rmargin=5) 


    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Script...", command=self.open_file)
        file_menu.add_command(label="Save Script...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def load_sample_script(self):
        sample_file_path = os.path.join(self.base_dir, "sample_script.txt")
        content = ""
        try:
            with open(sample_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = (
                "## ERROR: sample_script.txt not found.\n"
                "## Please create a file named 'sample_script.txt' in the application directory.\n\n"
                "TABLE: Example\n"
                "1:{1d6} Random result.\n"
            )
        except Exception as e:
            content = f"## ERROR loading sample_script.txt: {e}\n"

        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, content)

    def apply_shading(self, text_widget):
        text_widget.tag_remove("even_line", "1.0", "end")
        last_index = text_widget.index("end-1c")
        try:
            num_lines = int(last_index.split('.')[0])
        except ValueError:
            return 
        for i in range(1, num_lines + 1):
            if i % 2 == 0:
                text_widget.tag_add("even_line", f"{i}.0", f"{i}.end + 1c")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)
                self.refresh_table_list()
                self.apply_shading(self.input_text)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                content = self.input_text.get("1.0", tk.END)
                with open(file_path, "w") as f:
                    f.write(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def parse_and_insert_html(self, text_content):
        tokens = re.split(r'(<[^>]+>)', text_content)
        active_tags = set()
        table_start_index = None 
        
        for token in tokens:
            if not token: continue
            
            # Check if the token is an HTML tag
            if token.startswith("<") and token.endswith(">"):
                tag_lower = token.lower()
                
                # --- Block and Separator Tags (P, BR, HR) ---
                if tag_lower == "<br>": self.output_text.insert(tk.END, "\n")
                elif tag_lower == "<p>": self.output_text.insert(tk.END, "\n\n")
                elif tag_lower == "<hr>": self.output_text.insert(tk.END, "\n" + "—" * 40 + "\n")
                elif tag_lower == "<li>": self.output_text.insert(tk.END, "\n • ")
                
                # --- TABLE Tags ---
                elif tag_lower.startswith("<table"):
                    self.in_table = True
                    self.output_text.insert(tk.END, "\n")
                    table_start_index = self.output_text.index(tk.END + "-1c")
                    # Insert a wide placeholder to help the tag span correctly
                    self.output_text.insert(tk.END, " " * 80 + "\n") 
                    
                elif tag_lower.startswith("<tr"):
                    if self.in_table:
                        # Start a new row, ensuring a fresh line.
                        if table_start_index != self.output_text.index(tk.END + "-1c"):
                             # Insert a newline only if the current row isn't immediately after <table>
                             self.output_text.insert(tk.END, "\n")
                             
                # Check for start of <td> or <th> tag (handles attributes like colspan)
                elif token.lower().startswith("<td") or token.lower().startswith("<th"):
                    is_header = token.lower().startswith("<th")
                    if self.in_table:
                        
                        # 1. Parse colspan attribute from the full token
                        colspan_match = re.search(r'colspan\s*=\s*["\']?(\d+)["\']?', token, re.IGNORECASE)
                        colspan_value = int(colspan_match.group(1)) if colspan_match else 1
                        
                        # Insert a visual separator before the cell content
                        current_line_start = self.output_text.index("insert linestart")
                        current_pos = self.output_text.index("insert")
                        
                        # If we aren't at the start of the line, we need a separator
                        if current_pos != current_line_start:
                             self.output_text.insert(tk.END, " | ")

                        # 2. Apply extra visual padding for colspan
                        if colspan_value > 1:
                            # Insert spaces per extra column spanned
                            self.output_text.insert(tk.END, " " * 5 * (colspan_value - 1))
                            
                        # If it's a header, activate bold
                        if is_header: active_tags.add("bold")
                            
                        # Mark the start of the content inside the <td> tag
                        self.cell_content_start_index = self.output_text.index(tk.END)
                        
                elif tag_lower == "</td>" or tag_lower == "</th>": 
                    if self.in_table and self.cell_content_start_index:
                        # Apply the td_cell styling to everything since the last <td>
                        self.output_text.tag_add("td_cell", self.cell_content_start_index, self.output_text.index(tk.END))
                        
                        # If it was a header, deactivate bold (check against the closing tag)
                        if tag_lower == "</th>": active_tags.discard("bold")
                            
                        self.cell_content_start_index = None # Reset cell tracking
                        
                elif tag_lower == "</tr>":
                    if self.in_table:
                        # Add some space after the row for better visual separation of rows
                        self.output_text.insert(tk.END, " \n") 
                        
                elif tag_lower == "</table>":
                    if self.in_table:
                        self.in_table = False
                        
                        # Apply the 'table_border' tag to the entire block inserted since <table>
                        if table_start_index:
                            self.output_text.tag_add("table_border", table_start_index, self.output_text.index(tk.END))
                        self.output_text.insert(tk.END, "\n")
                        table_start_index = None
                        
                # --- Text Formatting Tags ---
                elif tag_lower.startswith("</"): # Closing tags
                    tag_name = tag_lower[2:-1]
                    if tag_name in ["b", "i", "u", "h1", "h2", "h3", "red", "blue"]:
                        # Convert simple tag names back to their full class names
                        full_tag_map = {"b": "bold", "i": "italic", "u": "underline", 
                                        "red": "red", "blue": "blue"}
                        full_tag_name = full_tag_map.get(tag_name, tag_name)
                        active_tags.discard(full_tag_name)
                        if full_tag_name.startswith("h"): self.output_text.insert(tk.END, "\n")

                elif tag_lower.startswith("<"): # Opening tags
                    tag_name = tag_lower[1:-1]
                    if tag_name == "b": active_tags.add("bold")
                    elif tag_name == "i": active_tags.add("italic")
                    elif tag_name == "u": active_tags.add("underline")
                    elif tag_name == "h1": active_tags.add("h1"); self.output_text.insert(tk.END, "\n")
                    elif tag_name == "h2": active_tags.add("h2"); self.output_text.insert(tk.END, "\n")
                    elif tag_name == "h3": active_tags.add("h3"); self.output_text.insert(tk.END, "\n")
                    elif tag_name == "red": active_tags.add("red")
                    elif tag_name == "blue": active_tags.add("blue")
                
            else:
                self.output_text.insert(tk.END, token, tuple(active_tags))
                
        # Final newline after parsing the content
        self.output_text.insert(tk.END, "\n")


    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = tk.Tk()
    app = IPPInterface(root, script_dir)
    root.mainloop()