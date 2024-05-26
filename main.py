import wx
import threading

from modules import create_gui, Simulation, MainFrame

def run(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations):
    new_simulation = Simulation(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations)
    new_simulation.run()


def run_tkinter_gui():
    root = create_gui(run)
    root.mainloop()

def run_wxpython_gui():
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    # Run each GUI in a separate thread
    tkinter_thread = threading.Thread(target=run_tkinter_gui)
    wxpython_thread = threading.Thread(target=run_wxpython_gui)

    tkinter_thread.start()
    wxpython_thread.start()

    # Wait for both threads to finish
    tkinter_thread.join()
    wxpython_thread.join()