class CombatLogger:
    LEVELS = {"minimum": 0, "action": 1, "proc": 2, "all": 3}

    def __init__(self, level="action"):
        self.level = self.LEVELS[level]
        self.logs = []

    def log(self, simulation_time, event, event_level="all"):
        self.logs.append({"time": simulation_time, "event": event})
        if self.level >= self.LEVELS[event_level]:
            print(f"{simulation_time}: {event}")

    def get_logs(self):
        return self.logs
