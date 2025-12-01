import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import random
import re

class IPPInterpreter:
    def __init__(self, root):
        self.root = root
        self.root.title("Inspiration Pad Pro Interpreter (Extended)")
        self.root.geometry("1000x700")

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
        self.input_text = tk.Text(left_frame, width=40, height=30, wrap=tk.WORD, undo=True)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # --- Center Widgets (Controls) ---
        
        # Table Selector
        tk.Label(control_frame, text="Start Table:", font=("Arial", 9)).pack(pady=(20, 5))
        self.table_selector = ttk.Combobox(control_frame, state="readonly", width=18)
        self.table_selector.pack(pady=5)
        
        # Refresh Button (to find tables in text)
        self.refresh_btn = tk.Button(control_frame, text="Scan/Refresh Tables", command=self.refresh_table_list)
        self.refresh_btn.pack(pady=5)
        
        # New: Run Count Input
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
        self.output_text = tk.Text(right_frame, width=40, height=30, wrap=tk.WORD, bg="#f0f0f0")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # --- Initial Data ---
        self.load_sample_script()
        self.refresh_table_list() # Populate dropdown initially

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
        sample = """Table: MasterTable
You encounter: [@Encounter]
Loot found: {1d4} gold pieces.
Mood: [|Happy|Sad|Angry|Confused|]

Table: Encounter
5: A group of {1d6} [@Humanoid]s
2: A solitary [@Humanoid]
A trap! (DC {1d20+5} to spot)

Table: Humanoid
Goblin
Kobold
Orc
Gnoll"""
        self.input_text.insert(tk.END, sample)

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
        Finds patterns like {1d6} or {1d20+5} and replaces them with rolled numbers.
        """
        # Pattern matches: { (number) d (number) (optional +/- number) }
        pattern = r"\{(\d+)d(\d+)([+-]\d+)?\}"
        
        def replace_match(match):
            count = int(match.group(1))
            sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            total = sum(random.randint(1, sides) for _ in range(count)) + modifier
            return str(total)

        # Keep replacing until no dice codes remain (though usually one pass is enough)
        return re.sub(pattern, replace_match, text)

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

        # 3. Resolve Dice {1d6} - We do this AFTER tables, so tables can contain dice
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
            start_table = list(tables.keys())[0]

        output_lines = []
        # Use num_runs for the loop count
        for _ in range(num_runs):
            base_text = self.roll_on_table(start_table, tables)
            final_text = self.process_text(base_text, tables)
            output_lines.append(final_text)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(output_lines))

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPPInterpreter(root)
    root.mainloop()