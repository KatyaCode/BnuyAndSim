from decimal import Decimal


class CurrentSimulationTime:
    _instance = None

    def __init__(self, value):
        self.value = Decimal(value)
        
    def __str__(self):
        return str(self.value)
    

    def __eq__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return self.value == other.value
        else:
            return self.value == Decimal(other)
        
    def __lt__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return self.value < other.value
        else:
            return self.value < Decimal(other)
        
    def __le__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return self.value <= other.value
        else:
            return self.value <= Decimal(other)
        
    def __gt__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return self.value > other.value
        else:
            return self.value > Decimal(other)
        
    def __ge__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return self.value >= other.value
        else:
            return self.value >= Decimal(other)
        
    def __add__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return CurrentSimulationTime(self.value + other.value)
        else:
            return CurrentSimulationTime(self.value + Decimal(other))

    def __iadd__(self, other):
        if isinstance(other, CurrentSimulationTime):
            self.value += other.value
        else:
            self.value += Decimal(other)
        return self
    def __sub__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return CurrentSimulationTime(self.value - other.value)
        else:
            return CurrentSimulationTime(self.value - Decimal(other))
        
    def __isub__(self, other):
        if isinstance(other, CurrentSimulationTime):
            self.value -= other.value
        else:
            self.value -= Decimal(other)
        return self
    
    def __mul__(self, other):
        if isinstance(other, CurrentSimulationTime):
            return CurrentSimulationTime(self.value * other.value)
        else:
            return CurrentSimulationTime(self.value * Decimal(other))
        
    def __imul__(self, other):
        if isinstance(other, CurrentSimulationTime):
            self.value *= other.value
        else:
            self.value *= Decimal(other)
        return self

    @staticmethod
    def get_instance():
        if CurrentSimulationTime._instance is None:
            CurrentSimulationTime._instance = CurrentSimulationTime(0)
        return CurrentSimulationTime._instance
    
    def reset(self):
        self.value = Decimal(0)


class CombatLogger:
    LEVELS = {"minimum": 0, "action": 1, "proc": 2, "all": 3}
    _instance = None

    @staticmethod
    def get_instance():
        if CombatLogger._instance is None:
            CombatLogger._instance = CombatLogger()
        return CombatLogger._instance

    def __init__(self, level="proc"):
        if self._instance is not None:
            raise Exception("This class is a singleton!")
        if level not in self.LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        self.level = self.LEVELS[level]
        self.current_simulation_time = CurrentSimulationTime.get_instance()
        self.logs = []

    def log(self, event, event_level="all"):
        self.logs.append(
            {"time": self.current_simulation_time, "event": event})
        if self.level >= self.LEVELS[event_level]:
            print(f"{self.current_simulation_time}: {event}")

    def get_logs(self):
        return self.logs
