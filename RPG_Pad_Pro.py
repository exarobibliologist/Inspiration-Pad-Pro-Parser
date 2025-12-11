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
        self.root.title("RPG Pad Pro (Modular Interface)")
        
        self.root.state('zoomed') 

        self.COLOR_ODD = "#FFFFFF"
        self.COLOR_EVEN = "#EFEFEF"
        self.RULESET_DIR = os.path.join(base_dir, "Rules") 
        self.ruleset_funcs = {} # Stores ALL dynamically loaded functions

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
        
        # INPUT STRIPING CONFIGURATION (Active for input editor)
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
        # Output is NOT zebra-striped
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
        """Creates the 'Rules' directory if it does not exist."""
        try:
            os.makedirs(self.RULESET_DIR, exist_ok=True)
        except OSError as e:
            messagebox.showerror("File System Error", f"Could not create ruleset directory '{self.RULESET_DIR}': {e}")
            
    def refresh_ruleset_list(self):
        """Scans the 'Rules' directory for subdirectories and populates the package selector."""
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
        """Safely loads a Python module from a given file path."""
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
        """Loads all functions from the selected ruleset folder into self.ruleset_funcs."""
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
        CORE_ENGINE_FUNCS = ['parse_tables', 'roll_on_table', 'resolve_table_tags', 'math_evaluator'] 
        if not all(func in self.ruleset_funcs for func in CORE_ENGINE_FUNCS):
            messagebox.showerror("Ruleset Error", f"The ruleset '{ruleset_name}' is missing one or more CORE ENGINE functions: {', '.join(CORE_ENGINE_FUNCS)}. Ensure 'table_parsing_rules.py' and 'math_rules.py' are present.")
            self.ruleset_funcs = {}
            
        self.refresh_table_list()


    # --- Generation Logic (Simplified Modular Calls) ---
    
    def refresh_table_list(self):
        """Uses the loaded parse_tables function to populate the table selector."""
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
        """Executes the generation process using loaded ruleset functions."""
        
        CORE_ENGINE_FUNCS = ['parse_tables', 'roll_on_table', 'resolve_table_tags', 'math_evaluator']
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

        for i in range(num_runs):
            base_text = roll_on_table_func(start_table, tables) 
            
            # Pass the entire ruleset dictionary as the 'helpers' argument
            final_text = resolve_table_tags_func(base_text, tables, self.ruleset_funcs) 
            
            self.parse_and_insert_html(final_text)

            if i < num_runs - 1:
                self.output_text.insert(tk.END, "═" * 40, "separator")
                self.output_text.insert(tk.END, "\n")
                
    # --- UI & Helper Methods ---
                
    def setup_output_tags(self):
        """Defines the visual styles for the HTML tags for the output window."""
        base_font = "Arial"
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
        sample = """##Example of In-line Picks: [|Happy|Sad|Angry|Confused|]
##Random Range uses two dashes: {20--90} degrees F.
##Example of Implode Command (Put delimiters in quotes): [@4 Table >> implode ", "]
## Advanced Math Test:
##{1d100+3} rolls a d100 and adds 3 to the answer
##{42+69} does math! 42+69=111
##{1d100-3} rolls a d100 and subtracts 3 from the answer
##{42-69} does math! 42-69=-27
##{42--69} picks a random number from 42 to 69
##{1d100*3} rolls a d100 and multiplies the answer by 3
##{1d100/3} rolls a d100 and divides the answer by 3. This will give you the accurate floating point calculation.
##{max(10, 50, 20)} returns the max value of a list of numbers.
##{min(10, 50, 20)} returns the min value of a list of numbers.
##{avg(10, 50, 20)} returns the average of a list of numbers.
##{sqrt(25)} returns the square root of a number.
##{abs(-10)} returns the absolute value of a number.
##{floor(10.9)} is rounded down.
##{ceil(10.1)} is rounded up.
##{sign(-5)} returns -1 for negative numbers, or 1 for positive numbers.

Table: MasterTable
<h1>The Dragon's Hoard</h1><br>You encounter: <b>[@Encounter]</b><hr><h3>Detailed Loot Analysis</h3><br>1. <b>Gold:</b> {sign(5)}  pieces.<br>2. <b>Item:</b> [@3 LootGen >> implode ", "].

Table: Encounter
A group of {2d100//5} [|Happy|Sad|Angry|Confused|] [@Humanoid]s.
A solitary <b>[@Humanoid]</b> (Elite).
<p>A hidden trap! (DC {1d20+5} to spot)</p>

Table: Humanoid
Goblin
Kobold
Orc
Gnoll

Table: MoneyMoneyMoney
42
69
100
{1d500}

Table: LootGen
[@LootTable] in [|pristine|enchanted|dirty|broken|cursed|unknown (DC {1d20} to identify)|] condition
[|pristine|enchanted|dirty|broken|cursed|unknown (DC {1d20} to identify)|] [@LootTable]

Table: LootTable
{round(sqrt({1d100000}))} gold pieces
wine skin [|(full of wine)|(full of hard liquor)|(empty)|(water)|]
bottle of hard liquor
bottle of [|fine|awful|] [|wine|beer|mead|]
small pouch of black lotus extract (about {1d100}% of the pouch is left)
religious [|medallion|icon|] worth ({1d10*10} sp)
lock of [|brunette|blonde|red|] hair
[|gold|silver|copper|steel|] [|ring|nose ring|neck chain|] with small {1d4*10}sp gem
feather from an exotic bird
[|squirrel|rabbit|racoon|jaguar|lion|tiger|] pelt
fishing hook and line
fishing net
bottle of ink ({1d100}% left) and quill
{1d3+1} sticks of chalk
pair of manacles
spade
[|sewing needle|sewing needle and some thread|]
{10-250} ft [|chain|silk rope|linen rope|]
small vial [|(empty)|(poison DC {1d10+10})|(sleeping draught)|(hallucinogen)|(unknown)|]
small [|leather|cloth|] bag with [|dice|figurine|] game
playing cards
small [|leather|cloth|] bag of herbs ([|poison DC {1d6+9}|sleeping aid|hallucinogen|unknown|healing|stimulant|medicinal|])
[|small|large|] bag of [|nuts and raisins|vegetables|jerky|grain|hard candy|stones|seashells|]
[|small|large|] bag of [|dead|live|] [|wasps|beetles|scorpions|spiders|ants|mice|]
hunting knife
whistle
drum
flute
metal cup
block of wax
{5-42} candles
list of names [|(some of them crossed off)|(and amounts owed)|]
some dirty sketches
[|clay|stone|brass|silver|gold|] figurine of a [|man|woman|horse|dragon|dog|lion|bird|phallic symbol|]
"""
        self.input_text.insert(tk.END, sample)

    def apply_shading(self, text_widget):
        """Applies zebra-striping ONLY to the provided text_widget (intended for input_text)."""
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
        for token in tokens:
            if not token: continue
            if token.startswith("<") and token.endswith(">"):
                tag_lower = token.lower()
                if tag_lower == "<br>": self.output_text.insert(tk.END, "\n")
                elif tag_lower == "<p>": self.output_text.insert(tk.END, "\n\n")
                elif tag_lower == "<hr>": self.output_text.insert(tk.END, "\n" + "-"*40 + "\n")
                elif tag_lower == "<li>": self.output_text.insert(tk.END, "\n • ")
                elif tag_lower == "<b>": active_tags.add("bold")
                elif tag_lower == "<i>": active_tags.add("italic")
                elif tag_lower == "<u>": active_tags.add("underline")
                elif tag_lower == "<h1>": self.output_text.insert(tk.END, "\n"); active_tags.add("h1")
                elif tag_lower == "<h2>": self.output_text.insert(tk.END, "\n"); active_tags.add("h2")
                elif tag_lower == "<h3>": self.output_text.insert(tk.END, "\n"); active_tags.add("h3")
                elif tag_lower == "<red>": active_tags.add("red")
                elif tag_lower == "<blue>": active_tags.add("blue")
                elif tag_lower == "</b>": active_tags.discard("bold")
                elif tag_lower == "</i>": active_tags.discard("italic")
                elif tag_lower == "</u>": active_tags.discard("underline")
                elif tag_lower == "</h1>": active_tags.discard("h1"); self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</h2>": active_tags.discard("h2"); self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</h3>": active_tags.discard("h3"); self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</red>": active_tags.discard("red")
                elif tag_lower == "</blue>": active_tags.discard("blue")
            else:
                self.output_text.insert(tk.END, token, tuple(active_tags))
        self.output_text.insert(tk.END, "\n")

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = tk.Tk()
    app = IPPInterface(root, script_dir)
    root.mainloop()