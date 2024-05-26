import wx

from modules import Simulation, MainFrame

def run(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations, callback=None):
    new_simulation = Simulation(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations)
    result = new_simulation.run()
    # Call the callback function if it was provided
    if callback is not None:
        wx.CallAfter(callback, result)

def run_wxpython_gui():
    app = wx.App(False)
    frame = MainFrame(run)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    run_wxpython_gui()