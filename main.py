import wx
import tracemalloc

from modules import Simulation, MainFrame, CombatLogger

def run(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations, callback=None):
    combat_logger = CombatLogger.get_instance()
    simulation = Simulation(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations)
    result = simulation.run()
    simulation = None
    combat_logger.clear()
    # Call the callback function if it was provided
    if callback is not None:
        wx.CallAfter(callback, result)

def run_wxpython_gui():
    app = wx.App(False)
    frame = MainFrame(run)
    frame.Show()
    app.MainLoop()
    
def print_memory_snapshot():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

if __name__ == "__main__":
    # tracemalloc.start()
    run_wxpython_gui()
    # print_memory_snapshot()