from decimal import Decimal

from . import effects


class Status():
    def __init__(self, applied_by, source, duration, applied_to):
        self.applied_by = applied_by
        self.source = source
        self.duration = duration
        self.applied_to = applied_to

    def update(self, time_step):
        raise NotImplementedError("Implement this in a subclass")
    
    
class Buff(Status):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        
    def __str__(self):
        raise NotImplementedError("Implement this in a subclass")
    
    def is_stackable(self):
        return False
    
    def consumed_by_ability(self):
        return False
    
    def update(self, time_step):
        self.duration -= time_step
        if self.duration <= 0:
            return False
        return self.duration


class Vanish(Buff):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyDamage("ALL", Decimal('0.3'))]

    def __str__(self):
        return "Vanish"

    def consumed_by_ability(self):
        return True


class Tranquility(Buff):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyDamage("ALL", Decimal('0.3'))]

    def __str__(self):
        return "Tranquility"
    
    
class Warcry(Buff):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyDamage("ALL", Decimal('0.2'))]

    def __str__(self):
        return "Warcry"
    
    
class RabbitLuck(Buff):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.IncreaseLuck(Decimal(1)), effects.GauranteeProcs()]
        
    def __str__(self):
        return "Rabbitluck"
    
    
class Haste(Buff):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyGCD(Decimal('0.8'))]
                        
    def __str__(self):
        return "Haste"
        
    def is_stackable(self):
        return True


class DamageOverTime(Status):
    def __init__(self, applied_by, source, duration, applied_to, damage):
        super().__init__(applied_by, source, duration, applied_to, damage)
        self.damage = damage

    def update(self, time_step):
        self.duration -= time_step
        if self.duration % 1 == 0:
            self.tick()
        if self.duration <= 0:
            return True
        return False

    def tick(self):
        self.applied_to.receive_effect_damage(
            self.damage, "dot", self.applied_by, self.source)
        
        
class Burn(Status):
    def __init__(self, applied_by, source, duration, applied_to, damage):
        super().__init__(applied_by, source, duration, applied_to)
        self.damage = damage

    def update(self, time_step):
        self.duration -= time_step
        if self.duration <= 0:
            self.activate()
            return False
        return self.duration
    
    def activate(self):
        self.applied_to.receive_effect_damage(
            self.damage, "burn", self.applied_by, self.source)

class RabbitSnare(Status):
    def __init__(self, applied_by, source, duration, applied_to, damage):
        super().__init__(applied_by, source, duration, applied_to)
        self.damage = damage

    def __str__(self):
        return "Rabbit Snare"

    def update(self, time_step):
        self.duration -= time_step
        if self.duration <= 0:
            self.activate()
            return False
        return self.duration

    def activate(self):
        self.applied_to.receive_effect_damage(
            self.damage, "debuff", self.applied_by, self.source)
        self.applied_by.actions["special"].restore_uses(1)


class TriSnare(RabbitSnare):
    def __init__(self, applied_by, source, duration, applied_to, damage):
        super().__init__(applied_by, source, duration, applied_to, damage)

    def __str__(self):
        return "Tri Snare"

    def activate(self):
        self.applied_to.receive_effect_damage(
            self.damage, "debuff", self.applied_by, self.source)
        self.applied_by.actions["special"].restore_uses("ALL")
        self.applied_by.actions["special"].add_charges(Decimal('1.5'), "ALL")
