import random
from decimal import Decimal

from . import effects


class Target:
    def __init__(self, name):
        self.name = name
        self.damage_received = []
        self.statuses = []

    def add_status(self, status):
        # Check if there is any status with the same class and source
        for existing_status in self.statuses:
            if type(existing_status) == type(status) and existing_status.source == status.source:
                return False

        # If there is no matching status, append the new status
        self.statuses.append(status)
        return True

    def update(self, time_step):
        status_durations = {}
        for status in self.statuses:
            if not status.update(time_step):
                self.statuses.remove(status)
            status_durations[str(status)] = str(status.duration)
        return status_durations

    def receive_action_damage(self, damage, character, source):
        actual_damage = self.calculate_variance(
            damage, character)
        self.apply_damage(actual_damage, character.name, source)
        return actual_damage

    def receive_effect_damage(self, damage, type, character, source):
        if type == 'burn':
            # Burn damage is always applied unmodified
            self.apply_damage(damage, character.name, source)
            return

        # Calculate the base damage
        damage_multiplier = Decimal(1)
        for effect in character.effects():
            if isinstance(effect, effects.MultiplyDamage):
                if type in effect.affected_sources:
                    damage_multiplier += effect.modifier

        if type == 'dot':
            actual_damage = damage * damage_multiplier
        else:
            actual_damage = self.calculate_variance(
                damage * damage_multiplier, character)

        self.apply_damage(actual_damage, character.name, source)

    def calculate_variance(self, damage, character):
        damage_variance = Decimal(random.uniform(0.85, 1.15))
        luck = character.luck()
        crit_chance = character.crit_chance + (luck / 2)
        crit_multiplier = character.crit_multiplier if random.random() <= crit_chance else Decimal(1)
        return damage * damage_variance * crit_multiplier

    def apply_damage(self, damage, character_name, source):
        damage_instance = {"damage": int(
            damage), "actor": character_name, "source": source}
        self.damage_received.append(damage_instance)
