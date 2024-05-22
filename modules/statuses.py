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


class Vanish(Status):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyDamage("ALL", Decimal('0.3'))]

    def __str__(self):
        return "Vanish"
    
    def is_stackable(self):
        return False

    def consumed_by_ability(self):
        return True

    def update(self, time_step):
        self.duration -= time_step
        if self.duration <= 0:
            return False
        return self.duration


class Tranquility(Status):
    def __init__(self, applied_by, source, duration, applied_to):
        super().__init__(applied_by, source, duration, applied_to)
        self.effects = [effects.MultiplyDamage("ALL", Decimal('0.3'))]

    def __str__(self):
        return "Tranquility"
    
    def is_stackable(self):
        return False

    def consumed_by_ability(self):
        return False

    def update(self, time_step):
        self.duration -= time_step
        if self.duration <= 0:
            return False
        return self.duration


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
