from decimal import Decimal
import copy


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
        action.perform(self, targets)
        if action.gcd > 0:
            self.global_cooldown = max(action.gcd, Decimal('0.3'))
        return action.name

    def act(self, targets):
        actions = []
        for action_name in self.actions:
            action = self.actions[action_name]
            if action.is_available(self) and action.is_automatic():
                self.perform_action(action_name, targets)
                actions.append(action.name)
        for action_name, condition in self.bunny_class["priority"]:
            if action_name == "defensive" and not self.use_defensive:
                continue
            if self.actions[action_name].is_available(self) and not self.actions[action_name].is_automatic() and condition(self, targets):
                self.perform_action(action_name, targets)
                actions.append(self.actions[action_name].name)
        if actions:
            return actions

    def update(self, time_step):
        current_cooldowns = {}
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
            status.update(time_step)
        return f"{self.name} has {current_cooldowns} remaining. GCD: {self.global_cooldown}"
    
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
    
    def effects(self):
        effects = []
        for action_name in self.actions:
            for effect in self.actions[action_name].effects:
                effects.append(effect)
        for status in self.statuses:
            for effect in status.effects:
                effects.append(effect)
        return effects
