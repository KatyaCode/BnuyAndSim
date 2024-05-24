import pytest
from itertools import product
from modules.simulation import Simulation
from modules.bunnies import bunny_classes

bunnies = [bunny_class for bunny_class in bunny_classes.values()]
upgrade_keys = ['primary', 'secondary', 'special', 'defensive']
upgrade_values = ['none', 'opal', 'sapphire', 'garnet', 'ruby', 'emerald']
upgrade_selections = []

# Add the case where all values are 'none'
upgrade_selections.append({key: 'none' for key in upgrade_keys})

# Add the cases where one value is not 'none' and the others are 'none'
for key in upgrade_keys:
    for value in upgrade_values:
        if value != 'none':
            upgrade_selections.append(
                {k: (value if k == key else 'none') for k in upgrade_keys})

# Generate all combinations of bunnies and upgrades
combinations = list(product(bunnies, upgrade_selections))


@pytest.mark.parametrize("bunny_class, selected_upgrades", combinations,
                         ids=[f"{bunny_class['name']} with {[value for value in selected_upgrades.values()]}" for bunny_class, selected_upgrades in combinations])
def test_run_with_all_upgrade_selections(bunny_class, selected_upgrades):
    simulation = Simulation(bunny_class, selected_upgrades, True, 1, 30, 1)
    simulation.run()
