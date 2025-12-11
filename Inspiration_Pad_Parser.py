# _____ _____  _____  _____ ____  _   _ _______ _____ _   _ _    _ ______ _____  
#|  __ \_   _|/ ____|/ ____/ __ \| \ | |__   __|_   _| \ | | |  | |  ____|  __ \ 
#| |  | || | | (___ | |   | |  | |  \| |  | |    | | |  \| | |  | | |__  | |  | |
#| |  | || |  \___ \| |   | |  | | . ` |  | |    | | | . ` | |  | |  __| | |  | |
#| |__| || |_ ____) | |___| |__| | |\  |  | |   _| |_| |\  | |__| | |____| |__| |
#|_____/_____|_____/ \_____\____/|_| \_|  |_|  |_____|_| \_|\____/|______|_____/ 
#                                                                                
#                                                                                
## _    _            _____  _____   _____   _____          _   _____                        
##| |  | |          |  __ \|  __ \ / ____| |  __ \        | | |  __ \                       
##| |  | |___  ___  | |__) | |__) | |  __  | |__) |_ _  __| | | |__) | __ ___   _ __  _   _ 
##| |  | / __|/ _ \ |  _  /|  ___/| | |_ | |  ___/ _` |/ _` | |  ___/ '__/ _ \ | '_ \| | | |
##| |__| \__ \  __/ | | \ \| |    | |__| | | |  | (_| | (_| | | |   | | | (_) || |_) | |_| |
## \____/|___/\___| |_|  \_\_|     \_____| |_|   \__,_|\__,_| |_|   |_|  \___(_) .__/ \__, |
##                                     ______             ______               | |     __/ |
##                                    |______|           |______|              |_|    |___/ 
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import random
import re

class IPPInterpreter:
    def __init__(self, root):
        self.root = root
        self.root.title("Inspiration Pad Pro Parser (HTML Extended)")
        
        # Maximize the window on startup
        self.root.state('zoomed') 

        # Define colors requested by the user
        self.COLOR_ODD = "#FFFFFF" # White
        self.COLOR_EVEN = "#EFEFEF" # Very Light Gray

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

        # Configure the 'even_line' tag for line shading on input
        self.input_text.tag_configure("even_line", background="#DDDDDD")
        self.input_text.bind("<KeyRelease>", lambda e: self.apply_shading(self.input_text))
        self.input_text.bind("<ButtonRelease>", lambda e: self.apply_shading(self.input_text))

        # --- Center Widgets (Controls) ---
        tk.Label(control_frame, text="Start Table:", font=("Arial", 9)).pack(pady=(20, 5))
        self.table_selector = ttk.Combobox(control_frame, state="readonly", width=18)
        self.table_selector.pack(pady=5)
        
        self.refresh_btn = tk.Button(control_frame, text="Scan Tables", command=self.refresh_table_list)
        self.refresh_btn.pack(pady=5)
        
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
        
        # 1. SETUP OUTPUT STYLES
        self.setup_output_tags()

        # --- Initial Data ---
        self.load_sample_script()
        self.refresh_table_list()
        self.apply_shading(self.input_text)

    def setup_output_tags(self):
        """Defines the visual styles for the HTML tags."""
        # Standard Shading
        self.output_text.tag_configure("even_line", background=self.COLOR_EVEN)
        
        # HTML Styles
        base_font = "Arial"
        self.output_text.tag_configure("bold", font=(base_font, 10, "bold"))
        self.output_text.tag_configure("italic", font=(base_font, 10, "italic"))
        self.output_text.tag_configure("underline", underline=True)
        
        # Headers
        self.output_text.tag_configure("h1", font=(base_font, 24, "bold"), spacing3=10)
        self.output_text.tag_configure("h2", font=(base_font, 16, "bold"), spacing3=5)
        self.output_text.tag_configure("h3", font=(base_font, 12, "bold"))
        
        # Colors
        self.output_text.tag_configure("red", foreground="red")
        self.output_text.tag_configure("blue", foreground="blue")
        self.output_text.tag_configure("green", foreground="green")
        self.output_text.tag_configure("gray", foreground="gray")

        # Separator Style
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
        sample = """##Example of Addition in Loot: {1d100+3} gold pieces.
##Example of Subtraction in Loot: {1d100-3} gold pieces.
##Example of Multiplication in Loot: {1d100*3} gold pieces.
##Example of Division (Floating Point) in Loot: {1d100/3} gold pieces.
##Example of Division (Integer) in Loot: {1d100//3} gold pieces.
##Example of In-line Picks: [|Happy|Sad|Angry|Confused|]
##Example of Random Range: {20-90} degrees F.
##Example of Implode Command (Put delimiters in quotes): [@4 Table >> implode ", "]

Table: MasterTable
<h1>The Dragon's Hoard</h1><br>You encounter: <b>[@Encounter]</b><hr><h3>Detailed Loot Analysis</h3><br>1. <b>Gold:</b> {1d100+50} pieces.<br>2. <b>Item:</b> [@3 LootGen >> implode ", "].

Table: Encounter
A group of {2d100//5} [|Happy|Sad|Angry|Confused|] [@Humanoid]s.
A solitary <b>[@Humanoid]</b> (Elite).
<p>A hidden trap! (DC {1d20+5} to spot)</p>

Table: Humanoid
Goblin
Kobold
Orc
Gnoll

Table: LootGen
[@LootTable] in [|pristine|enchanted|dirty|broken|cursed|unknown (DC {1d20} to identify)|] condition
[|pristine|enchanted|dirty|broken|cursed|unknown (DC {1d20} to identify)|] [@LootTable]

Table: LootTable
{314-1592} gold pieces
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
{2d10+10} ft [|chain|silk rope|linen rope|]
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
        text_widget.tag_remove("even_line", "1.0", "end")
        last_index = text_widget.index("end-1c")
        num_lines = int(last_index.split('.')[0])
        for i in range(1, num_lines + 1):
            if i % 2 == 0:
                text_widget.tag_add("even_line", f"{i}.0", f"{i}.end + 1c")

    # --- File Operations ---
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

    # --- Parsing Logic ---
    def parse_tables(self, script_content):
        tables = {}
        current_table_name = None
        lines = script_content.splitlines()
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.lower().startswith("table:"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    current_table_name = parts[1].strip()
                    tables[current_table_name] = []
                continue
            if current_table_name:
                weight = 1
                text_content = line
                if ":" in line:
                    parts = line.split(":", 1)
                    potential_weight = parts[0].strip()
                    if potential_weight.isdigit():
                        weight = int(potential_weight)
                        text_content = parts[1].strip()
                tables[current_table_name].append({"text": text_content, "weight": weight})
        return tables

    def refresh_table_list(self):
        script = self.input_text.get("1.0", tk.END)
        tables = self.parse_tables(script)
        table_names = list(tables.keys())
        self.table_selector['values'] = table_names
        if table_names:
            if self.table_selector.get() not in table_names:
                self.table_selector.current(0)
        else:
            self.table_selector.set("")

    # --- Generation Logic ---
    def roll_dice(self, text):
        dice_pattern = r"\{(\d+)d(\d+)(?:([\+\-\*]|//|\/)\s*(\d+))?\}" 
        def replace_dice_match(match):
            count = int(match.group(1))
            sides = int(match.group(2))
            operator = match.group(3)
            value_str = match.group(4)
            total = sum(random.randint(1, sides) for _ in range(count)) 
            if operator and value_str:
                try:
                    value = int(value_str)
                except ValueError: return "[Err]"
                if operator == '+': total += value
                elif operator == '-': total -= value
                elif operator == '*': total *= value
                elif operator == '//': total //= value if value != 0 else 1
                elif operator == '/': return f"{(float(total) / value):.2f}" if value != 0 else "Err"
            return str(total)
        
        text = re.sub(dice_pattern, replace_dice_match, text)
        range_pattern = r"\{(\d+)-(\d+)\}"
        def replace_range_match(match):
            mn = int(match.group(1))
            mx = int(match.group(2))
            return str(random.randint(mn, mx))
        text = re.sub(range_pattern, replace_range_match, text)
        return text

    def roll_on_table(self, table_name, tables):
        if table_name not in tables: return f"[Error: Table '{table_name}' not found]"
        entries = tables[table_name]
        if not entries: return "[Error: Table is empty]"
        population = [e['text'] for e in entries]
        weights = [e['weight'] for e in entries]
        return random.choices(population, weights=weights, k=1)[0]

    def process_text(self, text, tables, recursion_depth=0):
        if recursion_depth > 20: return "[Error: Max recursion depth]"
        while True:
            found_action = False
            table_match = re.search(r"\[@(.*?)\]", text)
            if table_match:
                full_tag = table_match.group(0) 
                content = table_match.group(1).strip()
                
                # Default separator is ""
                separator = "" 
                
                # NEW REGEX: Look for '>> implode "Separator"' 
                # Captures the content inside the quotes (group 1).
                implode_match = re.search(r'\s+>>\s+implode\s+"(.*?)"$', content, re.IGNORECASE)
                
                if implode_match:
                    # Capture the content exactly as it appears inside the quotes
                    separator = implode_match.group(1)
                    
                    # Remove the implode clause from the content to isolate count/table
                    content = content[:implode_match.start()].strip()
                    
                # --- END NEW LOGIC ---

                count = 1
                table_ref = content

                # 1. Try to match for Ranged/Dice count: {X} TableName
                multi_roll_match_dice = re.match(r"^(\{.*?\})\s+(.*)", content)
                
                if multi_roll_match_dice:
                    roll_expression = multi_roll_match_dice.group(1)
                    table_ref = multi_roll_match_dice.group(2).strip()
                    
                    # Roll the dice expression to get a resulting number string
                    count_str = self.roll_dice(roll_expression)
                    try:
                        count = max(0, int(count_str)) 
                    except ValueError:
                        count = 1 
                        table_ref = content
                        
                # 2. Try to match for Fixed Numeric count: N TableName
                else:
                    match_multi_num = re.match(r"^(\d+)\s+(.*)", content)
                    if match_multi_num:
                        count = int(match_multi_num.group(1))
                        table_ref = match_multi_num.group(2).strip()

                # 3. Handle generation and replacement
                results = []
                if table_ref in tables:
                    for _ in range(count):
                        results.append(self.roll_on_table(table_ref, tables))
                    
                    # Use the determined separator
                    final_result = separator.join(results)
                    
                    text = text.replace(full_tag, final_result, 1)
                    found_action = True
                else:
                    # Table not found, replace tag with error message
                    text = text.replace(full_tag, f"[Error: Table '{table_ref}' not found]", 1)
                    found_action = True
                
            
            opt_match = re.search(r"\[\|(.*?)\|\]", text)
            if opt_match:
                full_tag = opt_match.group(0)
                options = opt_match.group(1).split('|')
                text = text.replace(full_tag, random.choice(options), 1)
                found_action = True

            if not found_action: break
        text = self.roll_dice(text)
        return text

    # --- HTML Parsing & Insertion Logic ---

    def parse_and_insert_html(self, text_content):
        tokens = re.split(r'(<[^>]+>)', text_content)
        active_tags = set()
        
        for token in tokens:
            if not token: 
                continue

            if token.startswith("<") and token.endswith(">"):
                tag_lower = token.lower()
                
                # Block Elements
                if tag_lower == "<br>": self.output_text.insert(tk.END, "\n")
                elif tag_lower == "<p>": self.output_text.insert(tk.END, "\n\n")
                elif tag_lower == "<hr>": self.output_text.insert(tk.END, "\n" + "-"*40 + "\n")
                elif tag_lower == "<li>": self.output_text.insert(tk.END, "\n • ")
                
                # Styles
                elif tag_lower == "<b>": active_tags.add("bold")
                elif tag_lower == "<i>": active_tags.add("italic")
                elif tag_lower == "<u>": active_tags.add("underline")
                elif tag_lower == "<h1>": 
                    self.output_text.insert(tk.END, "\n")
                    active_tags.add("h1")
                elif tag_lower == "<h2>": 
                    self.output_text.insert(tk.END, "\n")
                    active_tags.add("h2")
                elif tag_lower == "<h3>": 
                    self.output_text.insert(tk.END, "\n")
                    active_tags.add("h3")
                elif tag_lower == "<red>": active_tags.add("red")
                elif tag_lower == "<blue>": active_tags.add("blue")

                # Closing Tags
                elif tag_lower == "</b>": active_tags.discard("bold")
                elif tag_lower == "</i>": active_tags.discard("italic")
                elif tag_lower == "</u>": active_tags.discard("underline")
                elif tag_lower == "</h1>": 
                    active_tags.discard("h1")
                    self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</h2>": 
                    active_tags.discard("h2")
                    self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</h3>": 
                    active_tags.discard("h3")
                    self.output_text.insert(tk.END, "\n")
                elif tag_lower == "</red>": active_tags.discard("red")
                elif tag_lower == "</blue>": active_tags.discard("blue")
            
            else:
                current_tags = tuple(active_tags)
                self.output_text.insert(tk.END, token, current_tags)

        self.output_text.insert(tk.END, "\n")

    def run_generation(self):
        script = self.input_text.get("1.0", tk.END)
        tables = self.parse_tables(script)

        if not tables:
            messagebox.showinfo("Info", "No tables found.")
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
            base_text = self.roll_on_table(start_table, tables)
            final_text = self.process_text(base_text, tables)
            
            self.parse_and_insert_html(final_text)

            # Insert Separator between runs
            if i < num_runs - 1:
                self.output_text.insert(tk.END, "═" * 40, "separator")
                self.output_text.insert(tk.END, "\n")

        self.apply_shading(self.output_text)

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
        self.apply_shading(self.output_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPPInterpreter(root)
    root.mainloop()