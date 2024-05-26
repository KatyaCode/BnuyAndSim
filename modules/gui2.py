import wx

from .bunnies import bunny_classes


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Bnuy & Sim")

        # Create a wx.Notebook instance
        notebook = wx.Notebook(self)

        # Create the setup tab and add it to the notebook
        setup_panel = self.create_setup_tab(notebook)
        notebook.AddPage(setup_panel, "Simulation Setup")

        # Create the output tab and add it to the notebook
        output_panel = self.create_output_tab(notebook)
        notebook.AddPage(output_panel, "Results")
        
        # Set the sizer for the window
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Fit()
        self.Centre()
        
        # Set the minimum size of the window to its current size
        self.SetMinSize(self.GetSize())

    def create_setup_tab(self, parent):
        panel = wx.Panel(parent)

        # Create the dropdown menu for class selection
        bunnies = [bunny_classes[bunny_class]["name"]
                   for bunny_class in bunny_classes]
        self.class_dropdown = wx.Choice(panel, choices=bunnies)
        self.class_dropdown.SetSelection(0)
        
        # Create the upgrade controls
        self.primary_upgrade = wx.RadioBox(panel, label="Primary", choices=["None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.secondary_upgrade = wx.RadioBox(panel, label="Secondary", choices=["None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.special_upgrade = wx.RadioBox(panel, label="Special", choices=["None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.defensive_upgrade = wx.RadioBox(panel, label="Defensive", choices=["None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        # Create the number entries
        self.num_targets = wx.SpinCtrl(
            panel, min=1, max=6, initial=1, size=(50, -1))
        self.sim_length = wx.SpinCtrl(
            panel, min=1, max=300, initial=60, size=(50, -1))
        self.num_sims = wx.SpinCtrl(
            panel, min=1, max=50, initial=1, size=(50, -1))

        # Create the run button
        self.run_button = wx.Button(panel, label="Run Simulation")
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)

        # Create sizers for the two columns
        sim_box = wx.StaticBox(panel, label="Simulation Parameters")
        sim_sizer = wx.StaticBoxSizer(sim_box, wx.VERTICAL)
        sim_grid = wx.FlexGridSizer(3, 2, 5, 5)

        char_box = wx.StaticBox(panel, label="Character Parameters")
        char_sizer = wx.StaticBoxSizer(char_box, wx.VERTICAL)

        # Add the controls to the simulation parameters column
        sim_grid.AddMany([(wx.StaticText(panel, label="Number of targets:"), 0, wx.ALL, 5),
                          (self.num_targets, 0, wx.ALL, 5),
                          (wx.StaticText(panel, label="Simulation Length:"), 0, wx.ALL, 5),
                          (self.sim_length, 0, wx.ALL, 5),
                          (wx.StaticText(
                              panel, label="Number of Simulations:"), 0, wx.ALL, 5),
                          (self.num_sims, 0, wx.ALL, 5)])
        sim_sizer.Add(sim_grid)

        # Add the controls to the character parameters column
        char_sizer.Add(self.class_dropdown, 0, wx.ALL, 5)
        char_sizer.Add(self.primary_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.secondary_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.special_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.defensive_upgrade, 0, wx.ALL, 5)
        
        # Create a larger font for the run button
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)  # Adjust the size (14 here) as needed
        self.run_button.SetFont(font)

        # Create a box sizer for the run button
        run_button_sizer = wx.BoxSizer(wx.VERTICAL)
        run_button_sizer.Add(self.run_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Arrange the columns in a grid
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(sim_sizer, pos=(0, 0))
        sizer.Add(char_sizer, pos=(0, 1))
        sizer.Add((0, 0), pos=(1, 0), flag=wx.EXPAND)  # Add an empty space that expands
        sizer.Add((0, 0), pos=(1, 1), flag=wx.EXPAND)  # Add an empty space that expands
        sizer.Add(run_button_sizer, pos=(2, 0), flag=wx.EXPAND)  # Add the run button below the simulation parameters column
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(1, 1)  # Make the second row expandable
        panel.SetSizerAndFit(sizer)

        return panel

    def create_output_tab(self, parent):
        panel = wx.Panel(parent)

        # Create the console output
        self.console = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Arrange the controls in a grid
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(self.console, pos=(0, 0), span=(8, 2), flag=wx.EXPAND)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(7, 1)
        panel.SetSizerAndFit(sizer)

        return panel

    def on_run(self, event):
        # Get the selected class
        selected_class_name = self.class_dropdown.GetValue()
        selected_class = next(value for key, value in bunny_classes.items(
        ) if value["name"] == selected_class_name)

        # Clear the console
        self.console.Clear()

        # Run the simulation
        # TODO: Implement the run_simulation function
        # run_simulation(selected_class)

        # Print a message to the console
        self.console.AppendText(f"Running simulation for {
                                selected_class_name}\n")
