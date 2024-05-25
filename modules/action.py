from decimal import Decimal
import random

from . import effects
from .combat_logger import CombatLogger


combat_logger = CombatLogger.get_instance()


class Action:
    def __init__(self, name, action_type, base_damage, base_cooldown, base_gcd, num_hits, max_uses=1, uses_per_cd=1, effects=[]):
        self.name = name
        self.action_type = action_type
        self.base_damage = base_damage
        self.base_cooldown = base_cooldown
        self.base_gcd = base_gcd
        self.num_hits = num_hits
        self.max_uses = max_uses
        self.effects = effects
        self.uses_per_cd = uses_per_cd
        self.current_uses = 0
        self.current_cooldown = 0
        self.charges = (0, 0)
        self.character = None

    def damage(self):
        damage_multiplier = Decimal(1)
        for effect in self.character.effects():
            if isinstance(effect, effects.MultiplyDamage):
                if self.action_type in effect.affected_sources:
                    damage_multiplier += effect.modifier
        return self.base_damage * damage_multiplier

    def cooldown(self):
        return self.base_cooldown

    def gcd(self):
        if self.base_gcd == 0:
            return 0
        gcd_multiplier = Decimal(1)
        for effect in self.character.effects():
            if isinstance(effect, effects.MultiplyGCD):
                gcd_multiplier *= effect.modifier
        return max(self.base_gcd * gcd_multiplier, Decimal('0.3'))

    def perform(self, targets):
        if not self.is_available():
            raise ValueError("Action is not available")
        additional_hits = 0
        for effect in self.effects:
            if isinstance(effect, effects.RandomAdditionalHits):
                if effects.random_proc(effect.probability, self.character):
                    additional_hits += effect.additional_hits
                    combat_logger.log(f'PROC: {self.name} additional hits: {effect.additional_hits}', event_level="proc")
            if isinstance(effect, effects.HitsMultipliedByUses):
                additional_hits += self.num_hits * (self.current_uses - 1)
        charge_multiplier = self.consume_charge()
        if self.base_damage > 0:
            for target in targets:
                action_applied_debuff = False
                num_hits = self.num_hits + additional_hits
                hit = 0
                while hit < num_hits:
                    damage_dealt = target.receive_action_damage(
                        self.damage() * charge_multiplier, self.character, self.name)
                    hit_applied_debuff = self.trigger_on_hit_effects(
                        target, damage_dealt)
                    if not action_applied_debuff and hit_applied_debuff:
                        action_applied_debuff = True
                        for e in self.effects:
                            if isinstance(e, effects.AdditionalHitsOnDebuff):
                                num_hits += e.num_hits
                    hit += 1
        self.consume_uses()
        self.character.consume_statuses()
        self.trigger_on_use_effects(targets)
        self.character.trigger_on_action_effects(self, targets)

    def begin_combat(self):
        if self.starts_on_cooldown():
            self.current_uses = 0
        else:
            self.current_uses = self.max_uses
        self.current_cooldown = self.cooldown()
        self.charges = (0, 0)

    def update(self, time_step):
        if self.cooldown() == 0 and not self.uses_counter() and self.current_uses < self.max_uses:
            self.current_uses = self.max_uses
        if self.current_cooldown > 0 and self.current_uses < self.max_uses:
            self.current_cooldown -= time_step
            if self.current_cooldown < 0:
                self.current_cooldown = 0
            if self.current_cooldown == 0:
                self.reset_cooldown(natural_reset=True)
        return self.current_cooldown, self.current_uses

    def reduce_cooldown(self, reduction):
        if not self.uses_counter() and not self.current_uses == self.max_uses:
            self.current_cooldown = max(self.current_cooldown - reduction, 0)
            if self.current_cooldown == 0:
                self.reset_cooldown()
        return self.current_cooldown, self.current_uses

    def reset_cooldown(self, natural_reset=False):
        if any(isinstance(effect, effects.CannotBeReset) for effect in self.effects) and not natural_reset:
            return
        self.current_cooldown = self.cooldown()
        self.current_uses = min(
            self.current_uses + self.uses_per_cd, self.max_uses)

    def restore_uses(self, amount=1):
        if any(isinstance(effect, effects.CannotBeRestored) for effect in self.effects):
            return self.current_uses
        if amount == "ALL":
            amount = self.max_uses
        self.current_uses = min(self.current_uses + amount, self.max_uses)
        if self.current_uses == self.max_uses:
            self.current_cooldown = self.cooldown()
        return self.current_uses

    def add_charges(self, charge_level, charge_amount, max_charges=1):
        if charge_amount == "ALL":
            charge_amount = self.max_uses
            max_charges = self.max_uses
        if self.charges[0] < charge_level:
            self.charges = (charge_level, charge_amount)
        elif self.charges[0] == charge_level:
            self.charges = (charge_level, min(
                self.charges[1] + charge_amount, max_charges))
        return self.charges

    def consume_uses(self):
        if any(isinstance(effect, effects.ConsumesAllUses) for effect in self.effects):
            self.current_uses = 0
        else:
            self.current_uses -= 1
        return self.current_uses

    def consume_charge(self):
        charge_multiplier = Decimal(1)
        if self.charges[1] > 0:
            charge_multiplier = self.charges[0]
            self.charges = (self.charges[0], self.charges[1] - 1)
            if self.charges[1] == 0:
                self.charges = (0, 0)
        return charge_multiplier

    def trigger_on_use_effects(self, targets):
        for effect in self.effects:
            if effect.effect_type == 'ON_USE':
                effect.trigger(self.character, targets)

    def trigger_on_hit_effects(self, target, damage_dealt):
        applied_debuff = False
        for effect in self.effects:
            if effect.effect_type == 'ON_HIT':
                if isinstance(effect, effects.AppliesDebuffOnHit):
                    success = effect.trigger(
                        self.character, target, damage_dealt)
                    if not applied_debuff and success:
                        applied_debuff = True
                else:
                    effect.trigger(self.character, target)
        return applied_debuff

    def has_charges(self, amount=1):
        """
        Check if the action has more than a specified number of charges
        
        Args:
            amount (int, optional): The number of charges to check for. Defaults to 1.
            
        Returns:
            bool: True if the action has at least the specified number of charges, False otherwise 
        """
        return self.charges[1] >= amount
    
    def base_damage_per_cast(self):
        return self.base_damage * self.num_hits * self.charges[0] if self.charges[0] > 0 else self.base_damage * self.num_hits
    
    def base_damage_per_second(self):
        if self.gcd() == 0:
            return self.base_damage_per_cast()
        return self.base_damage_per_cast() / self.gcd()

    def is_available(self):
        return self.current_uses > 0 and (self.gcd() == 0 or self.character.global_cooldown == 0)

    def starts_on_cooldown(self):
        return any(isinstance(effect, effects.StartOnCooldown) for effect in self.effects)

    def is_automatic(self):
        return any(isinstance(effect, effects.UsedAutomatically) for effect in self.effects)

    def uses_counter(self):
        return any((isinstance(effect, effects.UsesActionCounter) for effect in self.effects))

    def get_counter(self):
        for effect in self.effects:
            if isinstance(effect, effects.UsesActionCounter):
                return effect.current_value
        else:
            raise ValueError("Action does not have a counter")

    def increment_counter(self, amount=1):
        if self.uses_counter():
            for effect in self.effects:
                if isinstance(effect, effects.UsesActionCounter):
                    if effect.increment(amount):
                        self.reset_cooldown()
        else:
            raise ValueError("Action does not have a counter")
