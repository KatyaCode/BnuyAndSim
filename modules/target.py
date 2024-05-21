import random
from decimal import Decimal

from .effects import ModifyDamage


class Target:
    def __init__(self, name):
        self.name = name
        self.damage_received = []

    def receive_action(self, action, character, charge_multiplier=Decimal(1)):
        # Calculate the base damage
        damage_multiplier = Decimal(1)
        for a in character.actions.values():
            for effect in a.effects:
                if isinstance(effect, ModifyDamage):
                    if action.action_type in effect.affected_sources:
                        damage_multiplier += effect.modifier
        
        # Calculate the actual damage
        damage_variance = Decimal(random.uniform(0.85, 1.15))
        actual_damage = Decimal(action.damage) * damage_multiplier * charge_multiplier * damage_variance

        # Determine if the move crits
        if random.random() < character.crit_chance:
            actual_damage *= character.crit_multiplier

        damage_instance = {"damage": int(
            actual_damage), "actor": character.name, "source": action.name}
        self.damage_received.append(damage_instance)
