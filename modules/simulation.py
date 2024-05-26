from decimal import Decimal, ROUND_HALF_UP

from .target import Target
from .character import Character
from .combat_logger import CombatLogger, CurrentSimulationTime


class Simulation:
    def __init__(self, bunny_class, selected_upgrades, use_defensive=False, num_targets=1, simulation_time=200, num_simulations=1):
        self.bunny_class = bunny_class
        self.selected_upgrades = selected_upgrades
        self.use_defensive = use_defensive
        self.num_targets = num_targets
        self.simulation_time = Decimal(simulation_time)
        self.num_simulations = num_simulations
        self.current_simulation_time = CurrentSimulationTime.get_instance()
        self.time_step = Decimal('.1')

    def run(self):
        all_damage_averages = []

        for run in range(self.num_simulations):
            self.logger = CombatLogger.get_instance()
            self.character = Character(
                self.bunny_class, self.selected_upgrades, self.use_defensive)
            self.targets = [Target("Target {}".format(i+1))
                            for i in range(self.num_targets)]
            self.current_simulation_time.reset()
            self.character.begin_combat()
            character_actions = self.character.act(self.targets)
            if character_actions:
                self.logger.log(character_actions, event_level="action")
            while self.current_simulation_time + self.time_step < self.simulation_time:
                self.current_simulation_time += self.time_step  # increment simulated time
                self.character.update(self.time_step)
                for target in self.targets:
                    target.update(self.time_step)
                self.character.act(self.targets)
            self.current_simulation_time += self.time_step
            self.logger.log("Simulation complete", event_level="minimum")

            # Calculate total DPS and DPS from each source
            for target in self.targets:
                damage_totals = {}
                average_damages = {}
                for damage_instance in target.damage_received:
                    source = damage_instance["source"]
                    if source not in damage_totals:
                        damage_totals[source] = 0
                    damage_totals[source] += damage_instance["damage"]
                for source in damage_totals:
                    average_damages[(source, target.name, run+1)] = Decimal(damage_totals[source] /
                                                                            self.simulation_time).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                all_damage_averages.append(average_damages)

        # Collate DPS from each source
        average_of_averages = {}
        for damage_dict in all_damage_averages:
            for key in damage_dict:
                if key[:-2] not in average_of_averages:  # Exclude the run number from the key
                    average_of_averages[key[:-2]] = []
                average_of_averages[key[:-2]] += [damage_dict[key]]

        # Calculate the final averages and total
        final_averages = {key: Decimal(sum(value) / self.num_simulations).quantize(Decimal(
            '0.00'), rounding=ROUND_HALF_UP) for key, value in average_of_averages.items()}
        total_average = sum(final_averages.values())

        print("Final Averages:")
        for key, average in final_averages.items():
            print(f"{key}: {average}")
        print(f"Total Average: {total_average}")
        return total_average
