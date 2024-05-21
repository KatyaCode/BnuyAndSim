import tkinter as tk
import sys
import threading

from .bunnies import bunny_classes


class Console(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector()

    def redirector(self):
        sys.stdout = self

    def write(self, str):
        self.insert(tk.END, str)
        self.see(tk.END)


def create_gui(run):
    root = tk.Tk()
    root.title("Bnuy & Sim")
    
    vars = {}

    def validate_input(input):
        return input.isdigit() or input == ""
    
    def update_var(var_name, min_value, max_value):
        var = vars[var_name]
        value = var.get()
        if value == "":
            var.set(str(min_value))
        else:
            value = int(value)
            if value < min_value:
                var.set(str(min_value))
            elif value > max_value:
                var.set(str(max_value))

    # Configure the grid to expand with the window size
    root.columnconfigure(2, weight=1)
    root.rowconfigure(9, weight=1)

    # Get all dicts from bunnies.py
    bunnies = [bunny_classes[bunny_class]["name"]
               for bunny_class in bunny_classes]

    console = Console(root)
    console.grid(column=2, row=0, rowspan=10, sticky="nsew")

    # Create a StringVar for the class selection
    class_var = tk.StringVar(root)
    class_var.set(bunnies[0])  # Set the default value

    # Create the class selection drop-down
    class_menu = tk.OptionMenu(root, class_var, *bunnies)
    class_menu.grid(row=0, column=0, columnspan=2, sticky="ew")

    # Create the number of targets entry
    tk.Label(root, text="Number of targets:").grid(row=1, column=0)
    num_targets_var = tk.StringVar(root)
    vars["num_targets"] = num_targets_var
    num_targets_entry = tk.Entry(root, textvariable=num_targets_var)
    num_targets_var.set("1")  # Set the default value
    vcmd = (root.register(validate_input), '%P')
    num_targets_entry['validate'] = 'key'
    num_targets_entry['validatecommand'] = vcmd
    num_targets_var.trace_add('write', lambda *args: root.after_idle(lambda: update_var('num_targets', 1, 6)))
    num_targets_entry.grid(row=1, column=1)

    # Create the simulation length entry
    tk.Label(root, text="Simulation length:").grid(row=2, column=0)
    sim_length_var = tk.StringVar(root)
    vars["sim_length"] = sim_length_var
    sim_length_entry = tk.Entry(root, textvariable=sim_length_var)
    sim_length_var.set("200")  # Set the default value
    vcmd = (root.register(validate_input), '%P')
    sim_length_entry['validate'] = 'key'
    sim_length_entry['validatecommand'] = vcmd
    sim_length_var.trace_add('write', lambda *args: root.after_idle(lambda: update_var('sim_length', 1, 300)))
    sim_length_entry.grid(row=2, column=1)

    # Create the number of runs entry
    tk.Label(root, text="Number of runs:").grid(row=3, column=0)
    num_runs_var = tk.StringVar(root)
    vars["num_runs"] = num_runs_var
    num_runs_entry = tk.Entry(root, textvariable=num_runs_var)
    num_runs_var.set("5")  # Set the default value
    vcmd = (root.register(validate_input), '%P')
    num_runs_entry['validate'] = 'key'
    num_runs_entry['validatecommand'] = vcmd
    num_runs_var.trace_add('write', lambda *args: root.after_idle(lambda: update_var('num_runs', 1, 50)))
    num_runs_entry.grid(row=3, column=1)

    # Create the checkbox for "Use Defensive?"
    use_defensive_var = tk.BooleanVar()
    use_defensive_var.set(False)  # Set the default value
    tk.Checkbutton(root, text="Use Defensive?",
                   variable=use_defensive_var).grid(row=4, column=0, columnspan=2, sticky="w")

    # Create the options for the option menus
    options = ["None", "Opal", "Sapphire", "Garnet", "Ruby", "Emerald"]

    # Create the primary option menu
    primary_var = tk.StringVar(root)
    primary_var.set(options[0])  # Set the default value
    tk.Label(root, text="Primary Upgrade:").grid(row=5, column=0)
    primary_option_menu = tk.OptionMenu(root, primary_var, *options)
    primary_option_menu.grid(row=5, column=1)

    # Create the secondary option menu
    secondary_var = tk.StringVar(root)
    secondary_var.set(options[0])  # Set the default value
    tk.Label(root, text="Secondary Upgrade:").grid(row=6, column=0)
    secondary_option_menu = tk.OptionMenu(root, secondary_var, *options)
    secondary_option_menu.grid(row=6, column=1)

    # Create the special option menu
    special_var = tk.StringVar(root)
    special_var.set(options[0])  # Set the default value
    tk.Label(root, text="Special Upgrade:").grid(row=7, column=0)
    special_option_menu = tk.OptionMenu(root, special_var, *options)
    special_option_menu.grid(row=7, column=1)

    # Create the defensive option menu
    defensive_var = tk.StringVar(root)
    defensive_var.set(options[0])  # Set the default value
    tk.Label(root, text="Defensive Upgrade:").grid(row=8, column=0)
    defensive_option_menu = tk.OptionMenu(root, defensive_var, *options)
    defensive_option_menu.grid(row=8, column=1)

    def run_simulation():
        # Disable the run button
        button.config(state=tk.DISABLED)

        # Get the selected class, simulation length, and number of runs
        selected_class_name = class_var.get()
        selected_class = next(value for key, value in bunny_classes.items(
        ) if value["name"] == selected_class_name)
        num_targets = int(num_targets_var.get())
        sim_length = int(sim_length_var.get())
        num_runs = int(num_runs_var.get())
        use_defensive = use_defensive_var.get()
        selected_upgrades = {
            "primary": primary_var.get().lower(),
            "secondary": secondary_var.get().lower(),
            "special": special_var.get().lower(),
            "defensive": defensive_var.get().lower()
        }

        console.delete('1.0', tk.END)  # Clear the console
        run(selected_class, selected_upgrades, use_defensive, num_targets,
            sim_length, num_runs)  # Run the provided function

        # Re-enable the run button
        button.config(state=tk.NORMAL)

    # Create the run button
    button = tk.Button(root, text="Run", command=lambda: threading.Thread(
        target=run_simulation).start())
    button.grid(row=9, column=0, columnspan=2, sticky="new")

    return root
