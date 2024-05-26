import wx
import threading
import sys
import time

from .bunnies import bunny_classes


class ConsoleRedirect:
    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl
        self.buffer = ""
        self.line_count = 0
        self.last_update = time.time()

    def write(self, text):
        self.buffer += text
        self.line_count += text.count('\n')

        # Update the wx.TextCtrl every 0.1 seconds
        if time.time() - self.last_update >= 0.1:
            if self.text_ctrl:
                wx.CallAfter(self.text_ctrl.AppendText, self.buffer)
            self.buffer = ""
            self.line_count = 0
            self.last_update = time.time()
            
    def update_text_ctrl(self, text):
        # Append the new text
        current_text = self.text_ctrl.GetValue()
        new_text = current_text + text

        # Split the text into lines
        lines = new_text.split('\n')

        # Limit the number of lines
        if len(lines) > 1000:
            # Remove the oldest lines
            lines = lines[-1000:]

        # Update the text in the wx.TextCtrl
        self.text_ctrl.Clear()
        self.text_ctrl.AppendText('\n'.join(lines))


    def flush(self):
        if self.buffer:
            if self.text_ctrl:
                wx.CallAfter(self.text_ctrl.AppendText, self.buffer)
            self.buffer = ""
            self.line_count = 0


class MainFrame(wx.Frame):
    def __init__(self, run_simulation):
        wx.Frame.__init__(self, None, title="Bnuy & Sim")
        self.run_simulation = run_simulation
        self.current_run_dps = None
        self.previous_run_dps = None
        self.difference = None

        # Create a wx.Notebook instance
        self.notebook = wx.Notebook(self)

        # Create the setup tab and add it to the notebook
        self.setup_panel = self.create_setup_tab(self.notebook)
        self.notebook.AddPage(self.setup_panel, "Simulation Setup")

        # Create the output tab and add it to the notebook
        self.output_panel = self.create_output_tab(self.notebook)
        self.notebook.AddPage(self.output_panel, "Results")

        # Create the Console Redirect
        self.console_redirect = ConsoleRedirect(self.console)
        sys.stdout = self.console_redirect

        # Set the sizer for the window
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
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

        # Create a checkbox for the "Use Defensive?" variable
        self.use_defensive = wx.CheckBox(panel, label="Use Defensive?")
        self.use_defensive.SetValue(True)

        # Create the upgrade controls
        self.primary_upgrade = wx.RadioBox(panel, label="Primary", choices=[
                                           "None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.secondary_upgrade = wx.RadioBox(panel, label="Secondary", choices=[
                                             "None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.special_upgrade = wx.RadioBox(panel, label="Special", choices=[
                                           "None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.defensive_upgrade = wx.RadioBox(panel, label="Defensive", choices=[
                                             "None", "Opal", "Sapphire", "Ruby", "Garnet", "Emerald"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        # Create the number entries
        self.num_targets = wx.SpinCtrl(
            panel, min=1, max=6, initial=1, size=(50, -1))
        self.sim_length = wx.SpinCtrl(
            panel, min=1, max=300, initial=60, size=(50, -1))
        self.num_sims = wx.SpinCtrl(
            panel, min=1, max=1000, initial=1, size=(50, -1))

        # Create the run button
        self.run_button = wx.Button(panel, label="Run Simulation")
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)

        # Create sizers for the two columns
        sim_box = wx.StaticBox(panel, label="Simulation Parameters")
        sim_sizer = wx.StaticBoxSizer(sim_box, wx.VERTICAL)
        sim_grid = wx.FlexGridSizer(3, 2, 5, 5)

        char_box = wx.StaticBox(panel, label="Character Parameters")
        char_sizer = wx.StaticBoxSizer(char_box, wx.VERTICAL)

        # Create a horizontal box sizer for the class dropdown and the "Use Defensive?" checkbox
        class_defensive_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the class dropdown and the "Use Defensive?" checkbox to the horizontal box sizer
        class_defensive_sizer.Add(self.class_dropdown, 0, wx.ALL, 5)
        class_defensive_sizer.Add(self.use_defensive, 0, wx.ALL, 5)

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
        char_sizer.Add(class_defensive_sizer, 0, wx.ALL, 5)
        char_sizer.Add(self.primary_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.secondary_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.special_upgrade, 0, wx.ALL, 5)
        char_sizer.Add(self.defensive_upgrade, 0, wx.ALL, 5)

        # Create a larger font for the run button
        # Adjust the size (14 here) as needed
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.run_button.SetFont(font)

        # Create a box sizer for the run button
        run_button_sizer = wx.BoxSizer(wx.VERTICAL)
        run_button_sizer.Add(self.run_button, proportion=1,
                             flag=wx.EXPAND | wx.ALL, border=5)

        # Arrange the columns in a grid
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(sim_sizer, pos=(0, 0))
        sizer.Add(char_sizer, pos=(0, 1))
        # Add an empty space that expands
        sizer.Add((0, 0), pos=(1, 0), flag=wx.EXPAND)
        # Add an empty space that expands
        sizer.Add((0, 0), pos=(1, 1), flag=wx.EXPAND)
        # Add the run button below the simulation parameters column
        sizer.Add(run_button_sizer, pos=(2, 0), flag=wx.EXPAND)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(1, 1)  # Make the second row expandable
        panel.SetSizerAndFit(sizer)

        return panel

    def create_output_tab(self, parent):
        panel = wx.Panel(parent)

        # Create the console output
        self.console = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY )
        
        # Create the DPS display boxes
        current_run_box = wx.StaticBox(panel, label="Total Average DPS")
        self.current_run_dps_display = wx.StaticText(current_run_box)
        previous_run_box = wx.StaticBox(panel, label="Previous Run")
        self.previous_run_dps_display = wx.StaticText(previous_run_box)
        difference_box = wx.StaticBox(panel, label="Difference")
        self.difference_display = wx.StaticText(difference_box)
        
        # Increase the font size of the current run DPS display
        font = self.current_run_dps_display.GetFont()
        font.PointSize += 2
        font.SetWeight(wx.FONTWEIGHT_BOLD)  # Make the font bold
        self.current_run_dps_display.SetFont(font)
        
        # Arrange the DPS displays in their boxes
        current_run_box_sizer = wx.StaticBoxSizer(current_run_box, wx.VERTICAL)
        current_run_box_sizer.Add(self.current_run_dps_display, flag=wx.ALL | wx.CENTER, border=5)
        previous_run_box_sizer = wx.StaticBoxSizer(previous_run_box, wx.VERTICAL)
        previous_run_box_sizer.Add(self.previous_run_dps_display, flag=wx.ALL | wx.CENTER, border=5)
        difference_box_sizer = wx.StaticBoxSizer(difference_box, wx.VERTICAL)
        difference_box_sizer.Add(self.difference_display, flag=wx.ALL | wx.CENTER, border=5)

        # Redirect console output to the console output TextCtrl
        sys.stdout = ConsoleRedirect(self.console)

        # Arrange the controls in a grid
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(self.console, pos=(0, 0), span=(8, 3), flag=wx.EXPAND)
        sizer.Add(previous_run_box_sizer, pos=(8, 0))
        sizer.Add(difference_box_sizer, pos=(8, 1))
        sizer.Add(current_run_box_sizer, pos=(8, 2), flag=wx.EXPAND)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(7, 1)
        panel.SetSizerAndFit(sizer)

        return panel

    def on_run(self, event):
        # Move the current DPS to the previous DPS and clear the current DPS
        self.previous_run_dps = self.current_run_dps
        self.current_run_dps = None
        self.difference = None
        self.previous_run_dps_display.SetLabel(str(self.previous_run_dps) if self.previous_run_dps else "")
        self.difference_display.SetLabel("")
        self.current_run_dps_display.SetLabel("")
        
        # Get the selected class
        selected_class_name = self.class_dropdown.GetStringSelection()
        selected_class = next(value for key, value in bunny_classes.items(
        ) if value["name"] == selected_class_name)
        use_defensive = self.use_defensive.GetValue()
        selected_upgrades = {
            "primary": self.primary_upgrade.GetStringSelection().lower(),
            "secondary": self.secondary_upgrade.GetStringSelection().lower(),
            "special": self.special_upgrade.GetStringSelection().lower(),
            "defensive": self.defensive_upgrade.GetStringSelection().lower()
        }
        num_targets = self.num_targets.GetValue()
        sim_length = self.sim_length.GetValue()
        num_sims = self.num_sims.GetValue()

        # Clear the console
        self.console.Clear()

        # Switch to the output tab
        self.notebook.SetSelection(1)  # The index of the output tab is 1
        for child in self.setup_panel.GetChildren():
            child.Enable(False)

        # Run the simulation
        self.console.AppendText(f"Running simulation for {
                                selected_class_name}\n")
        simulation_thread = threading.Thread(target=self.run_simulation, args=(
            selected_class, selected_upgrades, use_defensive, num_targets, sim_length, num_sims, self.on_simulation_complete))
        simulation_thread.start()

    def on_simulation_complete(self, result):
        self.current_run_dps = result
        self.difference = self.current_run_dps - self.previous_run_dps if self.previous_run_dps else None
        self.difference_display.SetLabel(str(self.difference) if self.difference else "")
        self.current_run_dps_display.SetLabel(str(self.current_run_dps))
        self.console_redirect.flush()
        # Enable all the controls on the setup tab
        for child in self.setup_panel.GetChildren():
            child.Enable(True)
