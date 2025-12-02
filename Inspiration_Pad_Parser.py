import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import random
import re

class IPPInterpreter:
    def __init__(self, root):
        self.root = root
        self.root.title("Inspiration Pad Pro (Extended)")
        self.root.geometry("1000x700")

        # Define colors requested by the user
        self.COLOR_ODD = "#EEEEEE" # White
        self.COLOR_EVEN = "#CCCCCC" # Gray

        # --- Menu Bar (File I/O) ---
        self.create_menu()

        # --- Layout Containers ---
        # Main container
        main_container = tk.Frame(root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left side for editing the script
        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Center controls
        control_frame = tk.Frame(main_container, padx=10, width=150)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right side for output
        right_frame = tk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Left Widgets (Editor) ---
        tk.Label(left_frame, text="Script Editor", font=("Arial", 11, "bold")).pack(anchor="w")
        # High-contrast selection settings
        self.input_text = tk.Text(left_frame, width=40, height=30, wrap=tk.WORD, undo=True, bg=self.COLOR_ODD, 
                                  selectbackground="#007ACC", selectforeground="#FFFFFF")
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Configure the 'even_line' tag for line shading on input
        self.input_text.tag_configure("even_line", background=self.COLOR_EVEN)
        
        # Bind events to automatically update shading whenever text changes
        # Use a lambda to pass the widget reference to the shading function
        self.input_text.bind("<KeyRelease>", lambda e: self.apply_shading(self.input_text))
        self.input_text.bind("<ButtonRelease>", lambda e: self.apply_shading(self.input_text))

        # --- Center Widgets (Controls) ---
        
        # Table Selector
        tk.Label(control_frame, text="Start Table:", font=("Arial", 9)).pack(pady=(20, 5))
        self.table_selector = ttk.Combobox(control_frame, state="readonly", width=18)
        self.table_selector.pack(pady=5)
        
        # Refresh Button (to find tables in text)
        self.refresh_btn = tk.Button(control_frame, text="Scan/Refresh Tables", command=self.refresh_table_list)
        self.refresh_btn.pack(pady=5)
        
        # Run Count Input
        tk.Label(control_frame, text="Run X Times:", font=("Arial", 9)).pack(pady=(20, 5))
        self.run_count_entry = tk.Entry(control_frame, width=8, justify='center')
        self.run_count_entry.insert(0, "5") # Default value
        self.run_count_entry.pack(pady=5)

        # Generate Button
        self.generate_btn = tk.Button(control_frame, text="Generate  >>", command=self.run_generation, height=2, bg="#dddddd", font=("Arial", 10, "bold"))
        self.generate_btn.pack(pady=30)

        # Clear Output Button
        self.clear_btn = tk.Button(control_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.BOTTOM, pady=20)

        # --- Right Widgets (Output) ---
        tk.Label(right_frame, text="Output", font=("Arial", 11, "bold")).pack(anchor="w")
        # Set default background to COLOR_ODD for odd lines
        # High-contrast selection settings
        self.output_text = tk.Text(right_frame, width=40, height=30, wrap=tk.WORD, bg=self.COLOR_ODD,
                                   selectbackground="#007ACC", selectforeground="#FFFFFF")
        self.output_text.pack(fill=tk.BOTH, expand=True)
        # Configure the 'even_line' tag for line shading on output
        self.output_text.tag_configure("even_line", background=self.COLOR_EVEN)

        # --- Initial Data ---
        self.load_sample_script()
        self.refresh_table_list() # Populate dropdown initially
        self.apply_shading(self.input_text) # Apply initial shading to input

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
        sample = """Table: MasterPrompt
This is a table
Each line on this table is one part of a random list.
10: This line is weighted to show up more times in the list
{1d100} is an example of dice notation
{1d100+10} is an example of using addition with dice notation
{1d100-10} is an example of using subtraction with dice notation
{1d100*10} is an example of using multiplication with dice notation
{1d100/3} is an example of using floating-point division with dice notation
{1d100//3} is an example of using integer division with dice notation
{42-69} will pick a number between this range
You can nest [|random|interesting|odd|cool|] things in a list to increase the randomness
100: Use this to call a table - [@Encounter]

Table: Encounter
A group of {1d10+10} [|Happy|Sad|Angry|Confused|] [@Humanoid]s - On win, Loot found: [@LootGen].
A solitary [@Humanoid] - On win, Loot found: [@LootGen]
A trap! (DC {1d10+15} to spot)

Table: Humanoid
Goblin
Kobold
Orc
Gnoll

Table: LootGen
{314-1565} gold pieces
a wine skin [|(full of wine)|(full of hard liquor)|(empty)|(water)|]
a bottle of hard liquor
a bottle of [|fine|awful|] [|wine|beer|mead|]
a small pouch of black lotus extract (about {1d100}% of the pouch is left)
a religious [|medallion|icon|] worth ({1d10*10} sp)
a lock of [|brunette|blonde|red|] hair
a [|gold|silver|copper|steel|] [|ring|nose ring|neck chain|] with small {1d4*10}sp gem
a feather from an exotic bird
a [|squirrel|rabbit|racoon|jaguar|lion|tiger|] pelt
a fishing hook and line
a fishing net
a bottle of ink ({1d100}% left) and quill
{1d3+1} sticks of chalk
a pair of manacles
a spade
[|a sewing needle|a sewing needle and some thread|]
a {2d10+10} ft [|chain|silk rope|linen rope|]
a small vial [|(empty)|(poison DC {1d10+10})|(sleeping draught)|(hallucinogen)|(unknown)|]
a small [|leather|cloth|] bag with [|dice|figurine|] game
playing cards
a small [|leather|cloth|] bag of herbs ([|poison DC {1d6+9}|sleeping aid|hallucinogen|unknown|healing|stimulant|medicinal|])
a [|small|large|] bag of [|nuts and raisins|vegetables|jerky|grain|hard candy|stones|seashells|]
a [|small|large|] bag of [|dead|live|] [|wasps|beetles|scorpions|spiders|ants|mice|]
a hunting knife
a whistle
a drum
a flute
a metal cup
a block of wax
{5-42} candles]
a list of names [|(some of them crossed off)|(and amounts owed)|]
some dirty sketches
a [|clay|stone|brass|silver|gold|] figurine of a [|man|woman|horse|dragon|dog|lion|bird|phallic symbol|]
"""
        self.input_text.insert(tk.END, sample)

    # --- Line Shading Logic (Reusable) ---
    def apply_shading(self, text_widget):
        """Applies alternating background colors to lines in the given text widget, 
        making the background span the full width."""
        
        # 1. Remove all existing 'even_line' tags
        text_widget.tag_remove("even_line", "1.0", "end")

        # 2. Find the total number of lines
        # 'end-1c' gets the index of the last character
        last_index = text_widget.index("end-1c")
        # 'index("end").split(".")[0]' gets the line number of the last line
        num_lines = int(last_index.split('.')[0])
        
        # 3. Loop through lines and apply shading
        for i in range(1, num_lines + 1):
            if i % 2 == 0: # Check if the line number is even
                start_index = f"{i}.0"
                # CRITICAL FIX: Add " + 1c" to the end index to force the tag to the end 
                # of the line in the widget, even if the line is short.
                end_index = f"{i}.end" + " + 1c"
                text_widget.tag_add("even_line", start_index, end_index)


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
                self.apply_shading(self.input_text) # Apply shading after loading content
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
        """Parses script into a dict of {TableName: [entries]}."""
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
                
                tables[current_table_name].append({
                    "text": text_content,
                    "weight": weight
                })
        return tables

    def refresh_table_list(self):
        """Scans the text for table names and updates the dropdown."""
        script = self.input_text.get("1.0", tk.END)
        tables = self.parse_tables(script)
        table_names = list(tables.keys())
        
        self.table_selector['values'] = table_names
        
        if table_names:
            # If nothing is selected, select the first one
            if self.table_selector.get() not in table_names:
                self.table_selector.current(0)
        else:
            self.table_selector.set("")

    # --- Generation Logic ---

    def roll_dice(self, text):
        """
        Finds and resolves dice roll patterns ({XdY[+/-/*//]Z}) and range patterns ({Min-Max}).
        """
        
        # 1. Resolve standard Dice patterns: {XdY[+/-/*]Z} or {XdY[/|//]Z}
        # The regex now uses a non-capturing group (?:...) to allow for the operator
        # to be one character (+, -, *, /) or two characters (//).
        dice_pattern = r"\{(\d+)d(\d+)(?:([\+\-\*]|//|\/)\s*(\d+))?\}" 
        
        def replace_dice_match(match):
            count = int(match.group(1))
            sides = int(match.group(2))
            
            # The operator is now group 3, the value is group 4
            operator = match.group(3)
            value_str = match.group(4)
            
            total = sum(random.randint(1, sides) for _ in range(count)) 
            
            if operator and value_str:
                try:
                    value = int(value_str)
                except ValueError:
                    # Should not happen with the regex, but good practice
                    return f"[ERROR: Invalid modifier value {value_str}]"

                if operator == '+':
                    total += value
                elif operator == '-':
                    total -= value
                elif operator == '*':
                    total *= value
                elif operator == '//':
                    # Integer Division (Floor Division)
                    if value == 0:
                        return f"[DIVIDE BY ZERO ERROR: {match.group(0)}]"
                    total //= value
                elif operator == '/':
                    # Floating Point Division (Precise)
                    if value == 0:
                        return f"[DIVIDE BY ZERO ERROR: {match.group(0)}]"
                    
                    # Ensure floating-point calculation
                    result_float = float(total) / value
                    # Return formatted string with precision
                    return f"{result_float:.6f}"
                
            # If the result is an integer (from dice roll, +, -, *, //), return it as a string
            return str(total)

        # Apply dice rolling
        text = re.sub(dice_pattern, replace_dice_match, text)

        # 2. Resolve Range patterns: {Min-Max}
        # Pattern matches: { (number) - (number) }
        range_pattern = r"\{(\d+)-(\d+)\}"
        
        def replace_range_match(match):
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            
            # Simple error check for invalid range
            if min_val > max_val:
                return f"[{min_val}-{max_val} ERROR: Min > Max]"
            
            result = random.randint(min_val, max_val) # randint is inclusive
            return str(result)
        
        # Apply range rolling
        text = re.sub(range_pattern, replace_range_match, text)
        
        return text

    def roll_on_table(self, table_name, tables):
        if table_name not in tables:
            return f"[Error: Table '{table_name}' not found]"
        
        entries = tables[table_name]
        if not entries:
            return "[Error: Table is empty]"

        population = [e['text'] for e in entries]
        weights = [e['weight'] for e in entries]
        choice = random.choices(population, weights=weights, k=1)[0]
        return choice

    def process_text(self, text, tables, recursion_depth=0):
        if recursion_depth > 20: return "[Error: Max recursion depth]"
        
        # Loop to resolve recursive tags (Tables and Inline Options)
        while True:
            found_action = False

            # 1. Resolve Tables [@TableName]
            table_match = re.search(r"\[@(.*?)\]", text)
            if table_match:
                full_tag = table_match.group(0) 
                table_ref = table_match.group(1)
                result = self.roll_on_table(table_ref, tables)
                text = text.replace(full_tag, result, 1)
                found_action = True
            
            # 2. Resolve Inline Options [|Option1|Option2|]
            # Matches syntax: [| option1 | option2 |]
            opt_match = re.search(r"\[\|(.*?)\|\]", text)
            if opt_match:
                full_tag = opt_match.group(0)
                content = opt_match.group(1)
                # Split content by | to get options
                options = content.split('|')
                # Pick a random option
                choice = random.choice(options)
                text = text.replace(full_tag, choice, 1)
                found_action = True

            # If we didn't find any tables OR options to process in this pass, we stop
            if not found_action:
                break

        # 3. Resolve Dice {1d6} and Ranges {Min-Max}
        text = self.roll_dice(text)
        
        return text

    def run_generation(self):
        script = self.input_text.get("1.0", tk.END)
        tables = self.parse_tables(script)

        if not tables:
            messagebox.showinfo("Info", "No tables found.")
            return

        # Get the number of runs from the entry field and validate it
        try:
            num_runs = int(self.run_count_entry.get())
            if num_runs <= 0:
                messagebox.showerror("Input Error", "Number of runs must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for 'Run X Times'.")
            return

        # Get selected table
        start_table = self.table_selector.get()
        if not start_table or start_table not in tables:
            if tables:
                start_table = list(tables.keys())[0]
            else:
                messagebox.showinfo("Info", "No tables found to run.")
                return

        output_lines = []
        # Use num_runs for the loop count
        for _ in range(num_runs):
            base_text = self.roll_on_table(start_table, tables)
            final_text = self.process_text(base_text, tables)
            output_lines.append(final_text)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(output_lines))
        
        # Apply shading to the output text after generation
        self.apply_shading(self.output_text)

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
        # Re-apply shading after clearing (will just set the background of the remaining empty line)
        self.apply_shading(self.output_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPPInterpreter(root)
    root.mainloop()