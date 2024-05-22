import random
import copy
from decimal import Decimal


class Effect:
    EFFECTTYPES = ['ON_USE', 'ON_HIT', 'ON_DAMAGE', 'ON_COOLDOWN', 'ON_PROC', 'ON_UNIQUE',
                   'INITIAL', 'ATTRIBUTE', 'MODIFIER']

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


class UsesActionCounter(Effect):
    def __init__(self, max_value):
        self.current_value = 0
        self.max_value = max_value
        self.effect_type = 'ATTRIBUTE'

    def increment(self, amount):
        self.current_value += amount
        if self.current_value >= self.max_value:
            self.current_value = 0
            return True
        return False


class UsedAutomatically(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'


class HitsMultipliedByUses(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'


class CannotBeReset(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'


class CannotBeRestored(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'
        
        
class AdditionalHitsOnDebuff(Effect):
    def __init__(self, num_hits):
        self.num_hits = num_hits
        self.effect_type = 'ATTRIBUTE'


class MultiplyDamage(Effect):
    def __init__(self, affected_sources, modifier):
        self.modifier = modifier
        if affected_sources == "ALL":
            self.affected_sources = [
                "primary", "secondary", "special", "defensive", "loot", "debuff", "dot", "trigger"]
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
    def __init__(self, action_name, charge_amount=1, charge_level=Decimal('1.5'), max_charges=1, probability=1):
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
            

class AppliesBuffOnUse(TriggerableEffect):
    def __init__(self, source, buff, buff_args, probability=1):
        self.source = source
        self.buff = buff
        self.buff_args = buff_args
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random.random() <= self.probability:
            character.add_status(self.buff(
                applied_by=character, source=self.source, applied_to=character, **self.buff_args))


class ChargesAbilityOnHit(TriggerableEffect):
    def __init__(self, action_name, charge_amount=1, charge_level=Decimal('1.5'), max_charges=1, probability=1):
        self.action_name = action_name
        self.charge_amount = charge_amount
        self.charge_level = charge_level
        self.max_charges = max_charges
        self.probability = probability
        self.effect_type = 'ON_HIT'

    def trigger(self, character, _):
        if random.random() <= self.probability:
            character.actions[self.action_name].add_charges(
                self.charge_level, self.charge_amount, self.max_charges)


class AppliesDebuffOnHit(TriggerableEffect):
    def __init__(self, source, debuff, debuff_args, probability=1):
        self.source = source
        self.debuff = debuff
        self.debuff_args = debuff_args
        self.probability = probability
        self.effect_type = 'ON_HIT'

    def trigger(self, character, target):
        if random.random() <= self.probability:
            if target.add_status(self.debuff(
                    applied_by=character, source=self.source, applied_to=target, **self.debuff_args)):
                return True
        return False

