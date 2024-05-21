from modules import create_gui, Simulation

def run(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations):
    new_simulation = Simulation(bunny_class, selected_upgrades, use_defensive, num_targets, simulation_time, num_simulations)
    new_simulation.run()

root = create_gui(run)
root.mainloop()