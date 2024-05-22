from decimal import Decimal

from . import effects

class Action:
    def __init__(self, name, action_type, damage, cooldown, gcd, num_hits, max_uses=1, uses_per_cd=1, effects=[]):
        self.name = name
        self.action_type = action_type
        self.damage = damage
        self.cooldown = cooldown
        self.gcd = gcd
        self.num_hits = num_hits
        self.max_uses = max_uses
        self.effects = effects
        self.uses_per_cd = uses_per_cd
        self.current_uses = 0
        self.current_cooldown = 0
        self.charges = (0,0)

    def perform(self, character, targets):
        total_hits = 0
        if not self.is_available(character):
            raise ValueError("Action is not available")
        if any(isinstance(effect, effects.HitsMultipliedByUses) for effect in self.effects):
            total_hits = self.num_hits * self.current_uses
            self.current_uses = 0
        else:
            self.current_uses -= 1
        charge_multiplier = self.consume_charge()
        if self.damage > 0:
            for target in targets:
                applied_debuff = False
                num_hits = total_hits if total_hits else self.num_hits
                hit = 0
                while hit < num_hits:
                    target.receive_action_damage(self, character, charge_multiplier)
                    for effect in self.effects:
                        if effect.effect_type == 'ON_HIT':
                            if isinstance(effect, effects.AppliesDebuffOnHit):
                                if effect.trigger(character, target) and not applied_debuff:
                                    applied_debuff = True
                                    for e in self.effects:
                                        if isinstance(e, effects.AdditionalHitsOnDebuff):
                                            num_hits += e.num_hits
                            else:
                                effect.trigger(character, target)
                    hit += 1
        for status in character.statuses:
            if status.consumed_by_ability():
                character.statuses.remove(status)
        for effect in self.effects:
            if effect.effect_type == 'ON_USE':
                effect.trigger(character, targets)
                    
    def begin_combat(self):
        if self.starts_on_cooldown():
            self.current_uses = 0
        else:
            self.current_uses = self.max_uses
        self.current_cooldown = self.cooldown
        self.charges = (0,0)
        
    def update(self, time_step):
        if self.cooldown == 0 and not self.uses_counter() and self.current_uses < self.max_uses:
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
        self.current_cooldown = self.cooldown
        self.current_uses = min(self.current_uses + self.uses_per_cd, self.max_uses)
        
    def restore_uses(self, amount=1):
        if any(isinstance(effect, effects.CannotBeRestored) for effect in self.effects):
            return self.current_uses
        if amount == "ALL":
            amount = self.max_uses
        self.current_uses = min(self.current_uses + amount, self.max_uses)
        if self.current_uses == self.max_uses:
            self.current_cooldown = self.cooldown
        return self.current_uses
        
    def add_charges(self, charge_level, charge_amount, max_charges=1):
        if charge_amount == "ALL":
            charge_amount = self.max_uses
            max_charges = self.max_uses
        if self.charges[0] < charge_level:
            self.charges = (charge_level, charge_amount)
        elif self.charges[0] == charge_level:
            self.charges = (charge_level, min(self.charges[1] + charge_amount, max_charges))
        return self.charges
    
    def consume_charge(self):
        charge_multiplier = Decimal(1)
        if self.charges[1] > 0:
            charge_multiplier = self.charges[0]
            self.charges = (self.charges[0], self.charges[1] - 1)
            if self.charges[1] == 0:
                self.charges = (0,0)
        return charge_multiplier
            
    def is_available(self, character):
        return self.current_uses > 0 and (self.gcd == 0 or character.global_cooldown == 0)
    
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
                
        