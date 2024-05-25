import random
import copy
from decimal import Decimal

from . import statuses
from .combat_logger import CombatLogger

combat_logger = CombatLogger.get_instance()


def random_proc(probability, character):
    if probability == 1:
        return True
    luck = character.luck()
    # Luck increases the probability of proccing to a maximum of double the base probability, Rabbitluck guarantees procs
    if random.random() <= min(probability + luck, probability * 2) or any(isinstance(effect, GauranteeProcs) for effect in character.effects()):
        character.trigger_on_proc_effects()
        return True
    return False


class Effect:
    EFFECTTYPES = ['ON_USE', 'ON_HIT', 'ON_DAMAGE', 'ON_COOLDOWN', 'ON_ACTION', 'ON_PROC', 'ON_UNIQUE',
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


class DoesNotResetActions(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'
        
        
class RandomAdditionalHits(Effect):
    def __init__(self, additional_hits, probability):
        self.additional_hits = additional_hits
        self.probability = probability
        self.effect_type = 'ATTRIBUTE'
        
        
class ConsumesAllUses(Effect):
    def __init__(self):
        self.effect_type = 'ATTRIBUTE'


class MultiplyDamage(Effect):
    def __init__(self, affected_sources, modifier):
        self.modifier = modifier
        if affected_sources == "ALL":
            self.affected_sources = [
                "primary", "secondary", "special", "defensive", "loot", "debuff", "dot", "trigger"]
        elif isinstance(affected_sources, list):
            self.affected_sources = affected_sources
        else:
            raise TypeError("affected_sources must be a list or 'ALL'")
        self.effect_type = 'MODIFIER'


class MultiplyGCD(Effect):
    def __init__(self, modifier):
        self.modifier = modifier
        self.effect_type = 'MODIFIER'


class IncreaseLuck(Effect):
    def __init__(self, modifier):
        self.modifier = modifier
        self.effect_type = 'MODIFIER'


class GauranteeProcs(Effect):
    def __init__(self):
        self.effect_type = 'MODIFIER'


class CooldownResetByUse(TriggerableEffect):
    def __init__(self, name, triggering_actions, probability=1):
        self.name = name
        self.triggering_actions = triggering_actions
        self.probability = probability
        self.effect_type = 'ON_ACTION'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} reset the cooldown of {self.name}", "proc")
            character.actions[self.name].reset_cooldown()
            
            
class DealsDamageOnUse(TriggerableEffect):
    def __init__(self, damage, damage_type, damage_source, probability=1):
        self.damage = damage
        self.damage_type = damage_type
        self.damage_source = damage_source
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, targets):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} {self.damage_source} deals {self.damage}", "proc")
            for target in targets:
                target.receive_effect_damage(self.damage, self.damage_type, character, self.damage_source)


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
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} restored {self.amount} uses of {self.action_name}", "proc")
            character.actions[self.action_name].restore_uses(self.amount)


class ResetCooldownOnUse(TriggerableEffect):
    def __init__(self, action_name, probability=1):
        self.action_name = action_name
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} reset the cooldown of {self.action_name}", "proc")
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
    def __init__(self, action_name, charge_amount, charge_level=Decimal('1.5'), max_charges=1, probability=1, uses_per_charge=1):
        self.action_name = action_name
        self.charge_amount = charge_amount
        self.charge_level = charge_level
        self.max_charges = max_charges
        self.probability = probability
        self.uses_per_charge = uses_per_charge
        self.uses_counter = 0
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.uses_per_charge > 1:
                self.uses_counter += 1
                if self.uses_counter < self.uses_per_charge:
                    return False # Do not charge ability if it has not been used enough times
                self.uses_counter = 0 # Reset the counter
            character.actions[self.action_name].add_charges(
                self.charge_level, self.charge_amount, self.max_charges)
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} charged {self.action_name} with {self.charge_amount} charges", "proc")
            return True
        return False
    
    
class ChargesAndResetsAbilityOnUse(TriggerableEffect):
    def __init__(self, action_name, charge_amount=1, charge_level=Decimal('1.5'), max_charges=1, probability=1):
        self.action_name = action_name
        self.charge_amount = charge_amount
        self.charge_level = charge_level
        self.max_charges = max_charges
        self.probability = probability
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} charged and reset {self.action_name} with {self.charge_amount} charges", "proc")
            character.actions[self.action_name].add_charges(
                self.charge_level, self.charge_amount, self.max_charges)
            character.actions[self.action_name].reset_cooldown()


class AppliesBuffOnUse(TriggerableEffect):
    def __init__(self, source, buff, buff_args, probability=1, replace=False):
        self.source = source
        self.buff = buff
        self.buff_args = buff_args
        self.probability = probability
        self.replace = replace
        self.effect_type = 'ON_USE'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} applied {self.buff.__name__} to themselves", "proc")
            character.add_status(self.buff(
                applied_by=character, source=self.source, applied_to=character, **self.buff_args), self.replace)


class ChargesAbilityOnHit(TriggerableEffect):
    def __init__(self, action_name, charge_amount, charge_level=Decimal('1.5'), max_charges=1, probability=1):
        self.action_name = action_name
        self.charge_amount = charge_amount
        self.charge_level = charge_level
        self.max_charges = max_charges
        self.probability = probability
        self.effect_type = 'ON_HIT'

    def trigger(self, character, _):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} charged {self.action_name} with {self.charge_amount} charges", "proc")
            character.actions[self.action_name].add_charges(
                self.charge_level, self.charge_amount, self.max_charges)


class AppliesDebuffOnHit(TriggerableEffect):
    def __init__(self, source, debuff, debuff_args, probability=1):
        self.source = source
        self.debuff = debuff
        self.debuff_args = debuff_args
        self.probability = probability
        self.effect_type = 'ON_HIT'

    def trigger(self, character, target, damage_dealt):
        if random_proc(self.probability, character):
            if self.probability < 1:
                combat_logger.log(
                    f"PROC: {character.name} applied {self.debuff.__name__} to {target.name}", "proc")
            debuff_args = copy.deepcopy(self.debuff_args)
            if self.debuff is statuses.Burn:
                debuff_args['damage'] = damage_dealt
            if target.add_status(self.debuff(
                    applied_by=character, source=self.source, applied_to=target, **debuff_args)):
                return True
        return False
