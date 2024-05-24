from decimal import Decimal
import copy

from . import effects


class Character:
    def __init__(self, bunny_class, selected_upgrades, use_defensive=False):
        self.name = "Player 1"
        self.bunny_class = bunny_class
        self.selected_upgrades = selected_upgrades
        self.use_defensive = use_defensive
        self.global_cooldown = Decimal(0)
        self.crit_chance = Decimal('0.3')
        self.crit_multiplier = Decimal('1.75')
        self.statuses = []
        self.actions = copy.deepcopy(self.bunny_class["actions"])
        for action in self.actions.values():
            action.character = self
        for upgrade, selection in self.selected_upgrades.items():
            if selection != "none":
                for action_name in self.actions:
                    if action_name in self.bunny_class["upgrades"][upgrade][selection]:
                        for key in self.bunny_class["upgrades"][upgrade][selection][action_name]:
                            if key == 'effects_extend':
                                for effect in self.bunny_class["upgrades"][upgrade][selection][action_name][key]:
                                    self.actions[action_name].effects.append(
                                        copy.deepcopy(effect))
                            else:
                                setattr(
                                    self.actions[action_name], key, copy.deepcopy(self.bunny_class["upgrades"][upgrade][selection][action_name][key]))
                                
    def begin_combat(self):
        for action_name in self.actions:
            self.actions[action_name].begin_combat()
        self.global_cooldown = Decimal(0)
        self.statuses = []

    def perform_action(self, action_name, targets):
        action = self.actions[action_name]
        action.perform(targets)
        if action.gcd() > 0:
            self.global_cooldown = action.gcd()
        return action.name

    def act(self, targets):
        actions = []
        for action_name in self.actions:
            action = self.actions[action_name]
            if action.is_available() and action.is_automatic():
                self.perform_action(action_name, targets)
                actions.append(action.name)
        for action_name, condition in self.bunny_class["priority"]:
            if action_name == "defensive" and not self.use_defensive:
                continue
            if self.actions[action_name].is_available() and not self.actions[action_name].is_automatic() and condition(self, targets):
                self.perform_action(action_name, targets)
                actions.append(self.actions[action_name].name)
                break
        if actions:
            return actions

    def update(self, time_step):
        current_cooldowns = {}
        current_buffs = {}
        if self.global_cooldown > 0:
            self.global_cooldown -= time_step
            if self.global_cooldown < 0:
                self.global_cooldown = 0
        for action in self.actions.values():
            if action.uses_counter():
                current_cooldowns[action.action_type] = f"Available Uses {action.current_uses} Counter: {action.get_counter()}"
            else:
                action.update(time_step)
                current_cooldowns[action.action_type] = f"Available Uses {action.current_uses} Cooldown: {action.current_cooldown}"
        for status in self.statuses:
            remaining_duration = status.update(time_step)
            if not remaining_duration:
                self.statuses.remove(status)
            else:
                current_buffs[str(status)] = remaining_duration
        return f"{self.name} status: {current_cooldowns}, {current_buffs}, GCD: {self.global_cooldown}"
    
    def add_status(self, status):
        if status.is_stackable():
            for existing_status in self.statuses:
                if type(existing_status) == type(status) and existing_status.source == status.source:
                    return
        else:
            for existing_status in self.statuses:
                if type(existing_status) == type(status):
                    return
        self.statuses.append(status)
        
    def trigger_on_proc_effects(self):
        pass
    
    def trigger_on_action_effects(self, action, targets):
        for effect in self.effects():
            if effect.effect_type == 'ON_ACTION':
                if action.action_type in effect.triggering_actions:
                    if isinstance(effect, effects.CooldownResetByUse) and effects.DoesNotResetActions in action.effects:
                        continue
                    effect.trigger(self, targets)
    
    def consume_statuses(self):
        for status in self.statuses:
            if status.consumed_by_ability():
                self.statuses.remove(status)
        
    def has_status(self, status_type):
        for status in self.statuses:
            if type(status) == status_type:
                return True
        return False
    
    def luck(self):
        luck = Decimal('0')
        for effect in self.effects():
            if isinstance(effect, effects.IncreaseLuck):
                luck += effect.modifier
        return luck
    
    def effects(self):
        effects = []
        for action_name in self.actions:
            for effect in self.actions[action_name].effects:
                effects.append(effect)
        for status in self.statuses:
            for effect in status.effects:
                effects.append(effect)
        return effects
