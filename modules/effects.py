import random
import copy
from decimal import Decimal


class Effect:
    EFFECTTYPES = ['ON_USE', 'ON_HIT', 'ON_DAMAGE',
                   'ON_COOLDOWN', 'INITIAL', 'ATTRIBUTE', 'MODIFIER']

    def __deepcopy__(self, memo):
        # Create a new instance of the class
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # Copy all the attributes
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))

        return result


class TriggerableEffect(Effect):
    def trigger(self, character, targets):
        raise NotImplementedError("Subclasses must implement this method")


class StartOnCooldown(Effect):
    def __init__(self, action_name):
        self.effect_type = 'ATTRIBUTE'
        self.name = "START_ON_COOLDOWN"


class UsesActionCounter(Effect):
    def __init__(self, max_count):
        self.current_count = 0
        self.max_count = max_count
        self.effect_type = 'ATTRIBUTE'
        self.name = "COUNTER"

    def increment(self, amount):
        self.current_count += amount
        if self.current_count >= self.max_count:
            self.current_count = 0
            return True
        return False


class UsedAutomatically(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'
        self.name = "AUTOMATIC"


class ModifyDamage(Effect):
    def __init__(self, affected_sources, modifier):
        self.modifier = modifier
        if affected_sources == "ALL":
            self.affected_sources = [
                "primary", "secondary", "special", "defensive", "loot", "debuff", "trigger"]
        elif affected_sources.istype(list):
            self.affected_sources = affected_sources
        else:
            raise TypeError("affected_sources must be a list or 'ALL'")
        self.effect_type = 'MODIFIER'


class ReduceCooldownOnUse(TriggerableEffect):
    def __init__(self, action_name, reduction):
        self.action_name = action_name
        self.reduction = reduction
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        character.actions[self.action_name].reduce_cooldown(self.reduction)


class RestoreUseOnUse(TriggerableEffect):
    def __init__(self, action_name, probability=1, amount=1):
        self.action_name = action_name
        self.probability = probability
        self.amount = amount
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random.random() <= self.probability:
            character.actions[self.action_name].restore_uses(self.amount)
            
            
class ResetCooldownOnUse(TriggerableEffect):
    def __init__(self, action_name, probability=1):
        self.action_name = action_name
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random.random() <= self.probability:
            character.actions[self.action_name].reset_cooldown()


class IncrementsActionCounter(TriggerableEffect):
    def __init__(self, target_action_name, amount=1):
        self.target_action_name = target_action_name
        self.amount = amount
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        character.actions[self.target_action_name].increment_counter(
            self.amount)


class ChargesAbilityOnUse(TriggerableEffect):
    def __init__(self, action_name, charge_amount=1, charge_level=Decimal(1.5), max_charges=1, probability=1):
        self.action_name = action_name
        self.charge_amount = charge_amount
        self.charge_level = charge_level
        self.max_charges = max_charges
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random.random() <= self.probability:
            character.actions[self.action_name].add_charges(
                self.charge_level, self.charge_amount, self.max_charges)
