from decimal import Decimal

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
        if not self.is_available(character):
            raise ValueError("Action is not available")
        self.current_uses -= 1
        charge_multiplier = self.consume_charge()
        for effect in self.effects:
            if effect.effect_type == 'ON_USE':
                effect.trigger(character, targets)
        if self.damage > 0:
            for hit in range(self.num_hits):
                for target in targets:
                    target.receive_action(self, character, charge_multiplier)
                    
    def begin_combat(self):
        if self.starts_on_cooldown():
            self.current_uses = 0
        else:
            self.current_uses = self.max_uses
        self.current_cooldown = self.cooldown
        self.charges = (0,0)
        
    def update(self, time_step):
        if self.cooldown == 0 and not self.uses_counter() and not self.current_uses == self.max_uses:
            self.current_uses = self.max_uses
        if self.current_cooldown > 0:
            self.current_cooldown -= time_step
            if self.current_cooldown < 0:
                self.current_cooldown = 0
            if self.current_cooldown == 0:
                self.reset_cooldown()
        return self.current_cooldown, self.current_uses
        
    def reduce_cooldown(self, reduction):
        if not self.uses_counter() and not self.current_uses == self.max_uses:
            self.current_cooldown = max(self.current_cooldown - reduction, 0)
            if self.current_cooldown == 0:
                self.reset_cooldown()
        return self.current_cooldown, self.current_uses
        
    def reset_cooldown(self):
        self.current_cooldown = self.cooldown
        self.current_uses = min(self.current_uses + self.uses_per_cd, self.max_uses)
        
    def restore_uses(self, amount=1):
        self.current_uses = min(self.current_uses + amount, self.max_uses)
        if self.current_uses == self.max_uses:
            self.current_cooldown = self.cooldown
        return self.current_uses
        
    def add_charges(self, charge_level, charge_amount, max_charges=1):
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
        return any(effect.name == "START_ON_COOLDOWN" for effect in self.effects if effect.effect_type == 'ATTRIBUTE')
    
    def is_automatic(self):
        return any(effect.name == "AUTOMATIC" for effect in self.effects if effect.effect_type == 'ATTRIBUTE')
    
    def uses_counter(self):
        return any(effect.name == "COUNTER" for effect in self.effects if effect.effect_type == 'ATTRIBUTE')
    
    def increment_counter(self, amount=1):
        if self.uses_counter():
            for effect in self.effects:
                if effect.effect_type == 'ATTRIBUTE' and effect.name == "COUNTER":
                    if effect.increment(amount):
                        self.reset_cooldown()
        else:
            raise ValueError("Action does not have a counter")
                
        