from decimal import Decimal

from .effects import (ReduceCooldownOnUse, StartOnCooldown, RestoreUseOnUse, UsesActionCounter, HitsMultipliedByUses, CannotBeReset, CannotBeRestored, AdditionalHitsOnDebuff,
                      ResetCooldownOnUse, IncrementsActionCounter, UsedAutomatically, ChargesAbilityOnUse, MultiplyDamage, ChargesAbilityOnHit,
                      AppliesDebuffOnHit, AppliesBuffOnUse)
from . import statuses
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
            ("special", lambda character, targets: True),
            ("defensive",
             lambda character, targets: character.actions['secondary'].current_uses == 0),
            ("secondary", lambda character, targets:
                character.actions['special'].current_cooldown >= (8 if character.selected_upgrades.get('special') == 'ruby'
                                                                  else (6 if character.selected_upgrades.get('special') == 'opal'
                                                                        else 4
                                                                        )
                                                                  ) or character.actions['special'].uses_counter()
             ),
            ("primary", lambda character, targets: True)
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
                        "effects": [MultiplyDamage("ALL", Decimal('0.2'))]
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
            "secondary": Action("Rabbitsnare", "secondary", damage=100, cooldown=Decimal(0), gcd=Decimal('1.2'), num_hits=1,
                                effects=[AppliesDebuffOnHit("Rabbitsnare Debuff", statuses.RabbitSnare, {"damage": 150, "duration": 5})]),
            "special": Action("Barrage", "special", damage=90, cooldown=Decimal(10), gcd=Decimal('1.2'), num_hits=3, max_uses=3),
            "defensive": Action("Careful Aim", "defensive", damage=0, cooldown=Decimal(10), gcd=Decimal(0), num_hits=0,
                                effects=[ChargesAbilityOnUse("primary", 1, 2, 1)])
        },
        "priority": [
            ("secondary", lambda character, targets: all(not isinstance(
                status, statuses.RabbitSnare) for target in targets for status in target.statuses)),
            ("special", lambda character, targets: all(not isinstance(
                effect, HitsMultipliedByUses) for effect in character.actions["special"].effects)),
            ("special", lambda character,
             targets: character.actions["special"].current_uses == character.actions["special"].max_uses),
            ("defensive", lambda character, targets: True),
            ("primary", lambda character, targets: True),
            ("secondary", lambda character, targets: True)
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
                        "effects": [AppliesDebuffOnHit("Rabbitsnare Debuff", statuses.RabbitSnare, {"damage": 350, "duration": 5})]
                    }
                },
                "sapphire": {
                    "secondary": {
                        "damage": 70,
                        "effects_extend": [AdditionalHitsOnDebuff(3)]
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
                        "gcd": Decimal('0.6'),
                        "effects": [RestoreUseOnUse("special", amount=1), ChargesAbilityOnUse("special", charge_amount=1, charge_level=Decimal(2))]
                    }
                },
                "emerald": {
                    "secondary": {
                        "effects": [AppliesDebuffOnHit("Rabbitsnare Debuff", statuses.TriSnare, {"damage": 150, "duration": Decimal(8)})]
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
                        "effects": [CannotBeReset(), CannotBeRestored()]
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
                        "effects": [ChargesAbilityOnHit("primary", charge_level=Decimal(3), probability=Decimal('0.1'))]
                    }
                },
                "emerald": {
                    "special": {
                        "damage": 110,
                        "gcd": Decimal(1.8),
                        "effects": [HitsMultipliedByUses()]
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects": [MultiplyDamage("ALL", Decimal('0.3'))]
                    }
                },
                "sapphire": {
                    "defensive": {
                        "effects_extend": [AppliesBuffOnUse("defensive", statuses.Vanish, {'duration': Decimal(3)})]
                    }
                },
                "ruby": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects": [ChargesAbilityOnUse("primary", charge_amount=1, charge_level=Decimal(3))]
                    }
                },
                "garnet": {
                    "defensive": {
                        "effects_extend": [ChargesAbilityOnUse("secondary", charge_amount=1, charge_level=Decimal(2))]
                    }
                },
                "emerald": {
                    "defensive": {
                        "cooldown": Decimal(15),
                        "effects_extend": [AppliesBuffOnUse("defensive", statuses.Tranquility, {'duration': Decimal(8)})]
                    }
                }
            }
        }
    }
}
