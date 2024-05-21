from decimal import Decimal

from .effects import (ReduceCooldownOnUse, StartOnCooldown, RestoreUseOnUse, UsesActionCounter, ResetCooldownOnUse,
                      IncrementsActionCounter, UsedAutomatically, ChargesAbilityOnUse, ModifyDamage)
from .action import Action

bunny_classes = {
    """ "Placeholder_Bunny": {
        "name": "Placeholder Bunny",
        "actions": {
            "primary": Action("Placeholder Primary", "primary", damage=100, cooldown=Decimal(0), gcd=Decimal(1), num_hits=1, max_uses=1),
            "secondary": Action("Placeholder Secondary", "secondary", damage=100, cooldown=Decimal(2), gcd=Decimal('0.5'), num_hits=1, max_uses=2),
            "special": Action("Placeholder Special", "special", damage=500, cooldown=Decimal(5), gcd=Decimal(1), num_hits=1, max_uses=1)
        },
        "priority": [
            ("special", lambda character: True),
            ("secondary", lambda character: True),
            ("primary", lambda character: True)
        ]
    }, """
    "Ancient_Bunny": {
        "name": "Ancient Bunny",
        "actions": {
            "primary": Action("Strike Command", "primary", damage=70, cooldown=Decimal(0), gcd=Decimal('1.2'), num_hits=2),
            "secondary": Action("March Command", "secondary", damage=240, cooldown=Decimal(6), gcd=Decimal('1.2'), num_hits=1, max_uses=2, effects=[ReduceCooldownOnUse("special", 4)]),
            "special": Action("Abyssal Call", "special", damage=180, cooldown=Decimal(20), gcd=Decimal('1.2'), num_hits=4, effects=[StartOnCooldown("special")]),
            "defensive": Action("Protect Command", "defensive", damage=0, cooldown=Decimal(10), gcd=Decimal(0), num_hits=0, effects=[RestoreUseOnUse("secondary", 1)])
        },
        "priority": [
            ("special", lambda character: True),
            ("defensive",
             lambda character: character.actions['secondary'].current_uses == 0),
            ("secondary", lambda character:
                character.actions['special'].current_cooldown >= (8 if character.selected_upgrades.get('special') == 'ruby'
                                                                  else (6 if character.selected_upgrades.get('special') == 'opal'
                                                                        else 4
                                                                        )
                                                                  ) or character.actions['special'].uses_counter()
             ),
            ("primary", lambda character: True)
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "damage": 80,
                        "effects": [ReduceCooldownOnUse("special", 1)]
                    }
                },
                "sapphire": {
                    "primary": {
                        "damage": 80,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "primary": {
                        "damage": 180,
                        "num_hits": 1
                    }
                },
                "garnet": {
                    "primary": {
                        "damage": 90,
                        "effects": [RestoreUseOnUse("secondary", 0.3)]
                    }
                },
                "emerald": {
                    "primary": {
                        "damage": 200,
                        "num_hits": 1
                    }
                }
            },
            "secondary": {
                "opal": {
                    "secondary": {
                        "damage": 290,
                        "effects": [ReduceCooldownOnUse("special", 6)]
                    }
                },
                "sapphire": {
                    "secondary": {
                        "damage": 260,
                        "cooldown": Decimal(4),
                        "max_uses": 3
                    }
                },
                "ruby": {
                    "secondary": {
                        "damage": 350,
                        "cooldown": Decimal(10),
                        "effects": [ReduceCooldownOnUse("special", 8)]
                    }
                },
                "garnet": {
                    "secondary": {
                        "damage": 270,
                        "effects": [ResetCooldownOnUse("special", probability=0.5)]
                    }
                },
                "emerald": {
                    "secondary": {
                        "damage": 280,
                        "gcd": Decimal(0),
                        "effects": [UsedAutomatically()]
                    }
                }
            },
            "special": {
                "opal": {
                    "special": {
                        "damage": 300,
                        "num_hits": 2,
                        "cooldown": Decimal(11)
                    }
                },
                "sapphire": {
                    "special": {
                        "damage": 210,
                        "num_hits": 2,
                        "max_uses": 3,
                        "uses_per_cd": 3
                    }
                },
                "ruby": {
                    "special": {
                        "damage": 320,
                        "cooldown": Decimal(28)
                    }
                },
                "garnet": {
                    "special": {
                        "damage": 220,
                        "cooldown": Decimal(0),
                        "effects_extend": [UsesActionCounter(3)]
                    },
                    "secondary": {
                        "effects_extend": [IncrementsActionCounter("special")]
                    }
                },
                "emerald": {
                    "special": {
                        "damage": 220,
                        "cooldown": Decimal(16),
                        "effects_extend": [UsedAutomatically()]
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "cooldown": Decimal(14),
                        "effects": [RestoreUseOnUse("secondary", 2)]
                    }
                },
                "sapphire": {
                    "defensive": {
                        "cooldown": Decimal(6)
                    }
                },
                "ruby": {
                    "defensive": {
                        "effects": [ModifyDamage("ALL", Decimal(0.2))]
                    }
                },
                "garnet": {
                    "defensive": {
                        "damage": 250
                    }
                },
                "emerald": {
                    "defensive": {
                        "cooldown": Decimal(4)
                    }
                }
            }
        }
    },
    "Sniper Bunny": {
        "name": "Sniper Bunny",
        "actions": {
            "primary": Action("Arrowshot", "primary", damage=200, cooldown=Decimal(0), gcd=Decimal('1.5'), num_hits=1),
            # TODO Snare
            "secondary": Action("Rabbitsnare", "secondary", damage=100, cooldown=Decimal(0), gcd=Decimal('1.2'), num_hits=1),
            "special": Action("Barrage", "special", damage=90, cooldown=Decimal(10), gcd=Decimal('1.2'), num_hits=3, max_uses=3),
            "defensive": Action("Careful Aim", "defensive", damage=0, cooldown=Decimal(10), gcd=Decimal(0), num_hits=0, effects=[ChargesAbilityOnUse("primary", 1, 2, 1)])
        },
        "priority": [
            ("special", lambda character: True),
            ("defensive", lambda character: True),
            ("primary", lambda character: True),
            ("secondary", lambda character: True)
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "damage": 350,
                        "cooldown": Decimal(4),
                    }
                },
                "sapphire": {
                    "primary": {
                        "damage": 100,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "primary": {
                        "damage": 320,
                        "gcd": Decimal(2)
                    }
                },
                "garnet": {
                    "primary": {
                        "damage": 250
                    }
                },
                "emerald": {
                    "primary": {
                        "damage": 280
                    }
                }
            },
            "secondary": {
                "opal": {
                    "secondary": {
                        "effects": []  # TODO Buffed Snare
                    }
                },
                "sapphire": {
                    "secondary": {
                        "damage": 70
                    }
                },
                "ruby": {
                    "secondary": {
                        "damage": 500,
                        "cooldown": Decimal(6),
                        "effects": [RestoreUseOnUse("special", amount=1)]
                    }
                },
                "garnet": {
                    "secondary": {
                        "damage": 0,
                        "gcd": Decimal(0.6),
                        "effects": [RestoreUseOnUse("special", amount=1), ChargesAbilityOnUse("special", charge_amount=1, charge_level=2)]
                    }
                },
                "emerald": {
                    "secondary": {
                        "effects": []  # TODO Tri-snare
                    }
                }
            },
            "special": {
                "opal": {
                    "special": {
                        "damage": 130,
                        "cooldown": Decimal(20),
                        "max_uses": 6,
                        "uses_per_cd": 6,
                        "effects": []  # TODO Cannot be reset
                    }
                },
                "sapphire": {
                    "special": {
                        "damage": 110,
                        "cooldown": Decimal(8),
                        "num_hits": 2,
                        "uses_per_cd": 2
                    }
                },
                "ruby": {
                    "special": {
                        "damage": 200,
                        "num_hits": 2,
                        "gcd": Decimal(1.8)
                    }
                },
                "garnet": {
                    "special": {
                        "damage": 110,
                        "effects": []  # TODO Charges Ability On Hit
                    }
                },
                "emerald": {
                    "special": {
                        "damage": 110,
                        "gcd": Decimal(1.8),
                        "effects": []  # TODO Uses All Uses Per Use, Number of Hits Multiplied by Uses
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects": []  # TODO All Damage Increased
                    }
                },
                "sapphire": {
                    "defensive": {
                        "effects_extend": []  # TODO Gives Vanish
                    }
                },
                "ruby": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects": [ChargesAbilityOnUse("primary", charge_amount=1, charge_level=3)]
                    }
                },
                "garnet": {
                    "defensive": {
                        "effects_extend": [ChargesAbilityOnUse("secondary", charge_amount=1, charge_level=2)]
                    }
                },
                "emerald": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects_extend": []  # TODO Gives Tranquility
                    }
                }
            }
        }
    }
}
