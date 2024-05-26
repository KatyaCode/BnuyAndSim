from decimal import Decimal

from .effects import (ReduceCooldownOnUse, StartOnCooldown, RestoreUseOnUse, UsesActionCounter, HitsMultipliedByUses, CannotBeReset, CannotBeRestored, AdditionalHitsOnDebuff,
                      ResetCooldownOnUse, IncrementsActionCounter, UsedAutomatically, ChargesAbilityOnUse, MultiplyDamage, ChargesAbilityOnHit, CooldownResetByUse,
                      AppliesDebuffOnHit, AppliesBuffOnUse, DoesNotResetActions, DealsDamageOnUse, ConsumesAllUses, RandomAdditionalHits, ChargesAndResetsAbilityOnUse)
from . import statuses
from .action import Action

bunny_classes = {
    "ancient_bunny": {
        "name": "Ancient Bunny",
        "actions": {
            "primary": Action("Strike Command", "primary", base_damage=70, base_cooldown=Decimal(0), base_gcd=Decimal('1.2'), num_hits=2),
            "secondary": Action("March Command", "secondary", base_damage=240, base_cooldown=Decimal(6), base_gcd=Decimal('1.2'), num_hits=1, max_uses=2,
                                effects=[ReduceCooldownOnUse("special", 4)]),
            "special": Action("Abyssal Call", "special", base_damage=180, base_cooldown=Decimal(20), base_gcd=Decimal('1.2'), num_hits=4,
                              effects=[StartOnCooldown("special")]),
            "defensive": Action("Protect Command", "defensive", base_damage=0, base_cooldown=Decimal(10), base_gcd=Decimal(0), num_hits=1,
                                effects=[RestoreUseOnUse("secondary", 1)])
        },
        "priority": [
            ("special", lambda character, targets: True),
            ("defensive",
             lambda character, targets: character.actions['secondary'].current_uses == 0),
            ("secondary", lambda character, targets:
                character.actions['special'].current_cooldown >= sum(
                    effect.reduction for effect in character.actions['secondary'].effects if isinstance(effect, ReduceCooldownOnUse)
                ) + character.actions['secondary'].gcd()
             ),
            ("secondary", lambda character, targets:
                character.selected_upgrades.get('special') == 'garnet' and character.actions['special'].current_cooldown >= character.actions['secondary'].current_cooldown
            ),
            ("secondary", lambda character, targets:
                character.actions['secondary'].current_uses == character.actions['secondary'].max_uses
            ),
            ("primary", lambda character, targets: True)
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "base_damage": 80,
                        "effects": [ReduceCooldownOnUse("special", 1)]
                    }
                },
                "sapphire": {
                    "primary": {
                        "base_damage": 80,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "primary": {
                        "base_damage": 180,
                        "num_hits": 1
                    }
                },
                "garnet": {
                    "primary": {
                        "base_damage": 90,
                        "effects": [RestoreUseOnUse("secondary", Decimal('0.3'))]
                    }
                },
                "emerald": {
                    "primary": {
                        "base_damage": 200,
                        "num_hits": 1
                    }
                }
            },
            "secondary": {
                "opal": {
                    "secondary": {
                        "base_damage": 290,
                        "effects": [ReduceCooldownOnUse("special", 6)]
                    }
                },
                "sapphire": {
                    "secondary": {
                        "base_damage": 260,
                        "base_cooldown": Decimal(4),
                        "max_uses": 3
                    }
                },
                "ruby": {
                    "secondary": {
                        "base_damage": 350,
                        "base_cooldown": Decimal(10),
                        "effects": [ReduceCooldownOnUse("special", 8)]
                    }
                },
                "garnet": {
                    "secondary": {
                        "base_damage": 270,
                        "effects": [ResetCooldownOnUse("special", Decimal(0.5))]
                    }
                },
                "emerald": {
                    "secondary": {
                        "base_damage": 280,
                        "base_gcd": Decimal(0),
                        "effects": [UsedAutomatically()]
                    }
                }
            },
            "special": {
                "opal": {
                    "special": {
                        "base_damage": 300,
                        "num_hits": 2,
                        "base_cooldown": Decimal(11)
                    }
                },
                "sapphire": {
                    "special": {
                        "base_damage": 210,
                        "num_hits": 2,
                        "max_uses": 3,
                        "uses_per_cd": 3
                    }
                },
                "ruby": {
                    "special": {
                        "base_damage": 320,
                        "base_cooldown": Decimal(28)
                    }
                },
                "garnet": {
                    "special": {
                        "base_damage": 220,
                        "base_cooldown": Decimal(0),
                        "effects_extend": [UsesActionCounter(3)]
                    },
                    "secondary": {
                        "effects_extend": [IncrementsActionCounter("special")]
                    }
                },
                "emerald": {
                    "special": {
                        "base_damage": 220,
                        "base_cooldown": Decimal(16),
                        "effects_extend": [UsedAutomatically()]
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "base_cooldown": Decimal(14),
                        "effects": [RestoreUseOnUse("secondary", 2)]
                    }
                },
                "sapphire": {
                    "defensive": {
                        "base_cooldown": Decimal(6)
                    }
                },
                "ruby": {
                    "defensive": {
                        "effects": [MultiplyDamage("ALL", Decimal('0.2'))]
                    }
                },
                "garnet": {
                    "defensive": {
                        "base_damage": 250
                    }
                },
                "emerald": {
                    "defensive": {
                        "base_cooldown": Decimal(4)
                    }
                }
            }
        }
    },
    "sniper_bunny": {
        "name": "Sniper Bunny",
        "actions": {
            "primary": Action("Arrowshot", "primary", base_damage=200, base_cooldown=Decimal(0), base_gcd=Decimal('1.5'), num_hits=1),
            "secondary": Action("Rabbitsnare", "secondary", base_damage=100, base_cooldown=Decimal(0), base_gcd=Decimal('1.2'), num_hits=1,
                                effects=[AppliesDebuffOnHit("Rabbitsnare Debuff", statuses.RabbitSnare, {"damage": 150, "duration": 5})]),
            "special": Action("Barrage", "special", base_damage=90, base_cooldown=Decimal(10), base_gcd=Decimal('1.2'), num_hits=3, max_uses=3),
            "defensive": Action("Careful Aim", "defensive", base_damage=0, base_cooldown=Decimal(10), base_gcd=Decimal(0), num_hits=0,
                                effects=[ChargesAbilityOnUse("primary", charge_amount=1, charge_level=Decimal(2))])
        },
        "priority": [
            ("secondary", lambda character, targets:
                all(not isinstance(status, statuses.RabbitSnare) for target in targets for status in target.statuses)),
            ("special", lambda character, targets:
                all(not isinstance(effect, HitsMultipliedByUses) for effect in character.actions["special"].effects)),
            ("special", lambda character, targets:
                character.actions["special"].current_uses == character.actions["special"].max_uses),
            ("defensive", lambda character, targets: True),
            ("primary", lambda character, targets: True),
            ("secondary", lambda character, targets: True)
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "base_damage": 350,
                        "base_cooldown": Decimal(4),
                    }
                },
                "sapphire": {
                    "primary": {
                        "base_damage": 100,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "primary": {
                        "base_damage": 320,
                        "base_gcd": Decimal(2)
                    }
                },
                "garnet": {
                    "primary": {
                        "base_damage": 250
                    }
                },
                "emerald": {
                    "primary": {
                        "base_damage": 280
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
                        "base_damage": 70,
                        "effects_extend": [AdditionalHitsOnDebuff(3)]
                    }
                },
                "ruby": {
                    "secondary": {
                        "base_damage": 500,
                        "base_cooldown": Decimal(6),
                        "effects": [RestoreUseOnUse("special", amount=1)]
                    }
                },
                "garnet": {
                    "secondary": {
                        "base_damage": 0,
                        "base_gcd": Decimal('0.6'),
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
                        "base_damage": 130,
                        "base_cooldown": Decimal(20),
                        "max_uses": 6,
                        "uses_per_cd": 6,
                        "effects": [CannotBeReset(), CannotBeRestored()]
                    }
                },
                "sapphire": {
                    "special": {
                        "base_damage": 110,
                        "base_cooldown": Decimal(8),
                        "num_hits": 2,
                        "uses_per_cd": 2
                    }
                },
                "ruby": {
                    "special": {
                        "base_damage": 200,
                        "num_hits": 2,
                        "base_gcd": Decimal(1.8)
                    }
                },
                "garnet": {
                    "special": {
                        "base_damage": 110,
                        "effects": [ChargesAbilityOnHit("primary", charge_amount=1, charge_level=Decimal(3), probability=Decimal('0.1'))]
                    }
                },
                "emerald": {
                    "special": {
                        "base_damage": 110,
                        "base_gcd": Decimal(1.8),
                        "effects": [HitsMultipliedByUses(), ConsumesAllUses()]
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "base_cooldown": Decimal(15),
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
                        "base_cooldown": Decimal(15),
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
                        "base_cooldown": Decimal(15),
                        "effects_extend": [AppliesBuffOnUse("defensive", statuses.Tranquility, {'duration': Decimal(8)})]
                    }
                }
            }
        }
    },
    "dancer_bunny": {
        "name": "Dancer Bunny",
        "actions": {
            "primary": Action("Twirling Rose", "primary", base_damage=60, base_cooldown=Decimal(0), base_gcd=Decimal('1.2'), num_hits=2,
                              effects=[ChargesAbilityOnHit("secondary", charge_amount=2, charge_level=Decimal('1.5'), max_charges=2)]),
            "secondary": Action("Falling Petal", "secondary", base_damage=50, base_cooldown=Decimal(0), base_gcd=Decimal('1.2'), num_hits=2,
                                effects=[ChargesAbilityOnHit("primary", charge_amount=2, charge_level=Decimal('1.5'), max_charges=2)]),
            "special": Action("Lily Blossom", "special", base_damage=350, base_cooldown=Decimal(8), base_gcd=Decimal('1.2'), num_hits=1,
                              effects=[CooldownResetByUse("special", ["primary", "secondary"], probability=Decimal('0.3'))]),
            "defensive": Action("Golden Grace", "defensive", base_damage=0, base_cooldown=Decimal(15), base_gcd=Decimal(0), num_hits=0,
                                effects=[AppliesBuffOnUse("defensive", statuses.Warcry, {'duration': Decimal(5)})])
        },
        "priority": [
            ("defensive", lambda character, targets: all(
                not (isinstance(effect, AppliesBuffOnUse) and
                     effect.buff in [statuses.Warcry, statuses.RabbitLuck] and
                     character.has_status(effect.buff))
                for effect in character.actions['defensive'].effects)),
            ("special", lambda character, targets: True),
            ("primary", lambda character, targets:
                character.selected_upgrades.get('primary') == 'opal' and not character.actions['special'].has_charges()),
            ("secondary", lambda character, targets:
                not character.actions['primary'].has_charges() and not character.actions['secondary'].has_charges()),
            ("primary", lambda character, targets:
                character.actions['primary'].base_damage_per_second() > character.actions['secondary'].base_damage_per_second()),
            ("secondary", lambda character, targets:
                character.actions['secondary'].base_damage_per_second() >= character.actions['primary'].base_damage_per_second()),
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "base_damage": 0,
                        "effects": [ChargesAbilityOnUse("secondary", charge_amount=4, max_charges=4),
                                    ChargesAbilityOnUse("special", charge_amount=1, charge_level=Decimal(2))]
                    }
                },
                "sapphire": {
                    "primary": {
                        "base_damage": 50,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "primary": {
                        "base_damage": 60,
                        "num_hits": 4,
                        "base_gcd": Decimal(4)
                    }
                },
                "garnet": {
                    "primary": {
                        "effects_extend": [DealsDamageOnUse(60, 'primary', 'Twirling Rose', Decimal('0.5'))]
                    }
                },
                "emerald": {
                    "primary": {
                        "base_damage": 80
                    }
                }
            },
            "secondary": {
                "opal": {
                    "secondary": {
                        "base_damage": 70,
                        "effects_extend": [ChargesAbilityOnUse('special', charge_amount=1, uses_per_charge=2)]
                    }
                },
                "sapphire": {
                    "secondary": {
                        "base_damage": 60,
                        "effects_extend": [RandomAdditionalHits(2, Decimal('0.4'))]
                    }
                },
                "ruby": {
                    "secondary": {
                        "base_damage": 85
                    }
                },
                "garnet": {
                    "secondary": {
                        "effects_extend": [ResetCooldownOnUse("defensive", probability=Decimal('0.4'))]
                    }
                },
                "emerald": {
                    "secondary": {
                        "base_gcd": 0,
                        "base_cooldown": Decimal(6),
                        "effects": [ChargesAbilityOnUse("primary", charge_amount=4, max_charges=4),
                                    UsedAutomatically(), DoesNotResetActions()]
                    }
                }
            },
            "special": {
                "opal": {
                    "special": {
                        "base_cooldown": Decimal(4),
                        "effects": []
                    }
                },
                "sapphire": {
                    "special": {
                        "base_damage": 140,
                        "num_hits": 3
                    }
                },
                "ruby": {
                    "special": {
                        "effects_extend": [AppliesDebuffOnHit("Lily Blossom Burn", statuses.Burn, {'duration': Decimal(5)})]
                    }
                },
                "garnet": {
                    "special": {
                        "effects": [CooldownResetByUse("special", ["primary", "secondary"], probability=Decimal('0.5'))]
                    }
                },
                "emerald": {
                    "special": {
                        "base_damage": 500,
                        "base_cooldown": Decimal(99)
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "effects_extend": [AppliesBuffOnUse("defensive", statuses.Haste, {'duration': Decimal(5)})]
                    }
                },
                "sapphire": {
                    "defensive": {
                        "effects_extend": [AppliesBuffOnUse("defensive", statuses.Vanish, {'duration': Decimal(5)})]
                    }
                },
                "ruby": {},
                "garnet": {
                    "defensive": {
                        "effects": [CannotBeReset(), AppliesBuffOnUse("defensive", statuses.RabbitLuck, {'duration': Decimal(5)})]
                    }
                },
                "emerald": {
                    "defensive": {
                        "effects": [MultiplyDamage("ALL", Decimal('0.1'))]
                    }
                }
            }
        }
    },
    "wizard_bunny": {
        "name": "Wizard Bunny",
        "actions": {
            "primary": Action("Dimi Moonburst", "primary", base_damage=200, base_cooldown=Decimal(0), base_gcd=Decimal('1.5'), num_hits=1),
            "secondary": Action("Lat Moonburst", "secondary", base_damage=120, base_cooldown=Decimal(0), base_gcd=Decimal('1.2'), num_hits=1,
                                effects=[ChargesAbilityOnHit("special", charge_amount=1, charge_level=Decimal('1.5'))]),
            "special": Action("Astral Swirl", "special", base_damage=280, base_cooldown=Decimal(7), base_gcd=Decimal('1.2'), num_hits=1,
                              effects=[CooldownResetByUse("special", ["primary"], probability=Decimal('0.3'))]),
            "defensive": Action("Astral Seal", "defensive", base_damage=0, base_cooldown=Decimal(15), base_gcd=Decimal(0), num_hits=0,
                                effects=[AppliesBuffOnUse("defensive", statuses.BuffingField, {'duration': Decimal(7), 'buff': statuses.Haste}, replace=True)])
        },
        "priority": [
            ("defensive", lambda character, targets: True),
            ("primary", lambda character, targets: 
                character.actions['primary'].base_damage_per_second() > character.actions['special'].base_damage_per_second()),
            ("secondary", lambda character, targets:
                not character.actions['special'].has_charges()),
            ("special", lambda character, targets: True),
            ("secondary", lambda character, targets:
                character.selected_upgrades.get('secondary') == 'emerald' and not character.actions['primary'].has_charges()),
            ("primary", lambda character, targets: True),
            ("secondary", lambda character, targets: True)
        ],
        "upgrades": {
            "primary": {
                "opal": {
                    "primary": {
                        "base_damage": 400,
                        "base_cooldown": Decimal(4)
                    }
                },
                "sapphire": {
                    "primary": {
                        "base_damage": 140,
                        "base_gcd": Decimal('0.8')
                    }
                },
                "ruby": {
                    "primary": {
                        "base_damage": 280
                    }
                },
                "garnet": {
                    "primary": {
                        "effects": [AppliesBuffOnUse("primary", statuses.Warcry, {'duration': Decimal(5)}, probability=Decimal('0.3'))]
                    }
                },
                "emerald": {
                    "primary": {
                        "base_damage": 220
                    }
                }
            },
            "secondary": {
                "opal": {
                    "secondary": {
                        "base_damage": 0,
                        "effects": [ChargesAbilityOnHit("special", charge_amount=1, charge_level=Decimal(2))]
                    }
                },
                "sapphire": {
                    "secondary": {
                        "base_damage": 180,
                        "base_cooldown": Decimal(8),
                        "max_uses": 3,
                        "effects_extend": [MultiplyDamage(["secondary"], Decimal('0.3'))] #Backstab is implemented as a .3 Multiply Damage effect as it always triggers on bosses
                    }
                },
                "ruby": {
                    "secondary": {
                        "base_damage": 250,
                        "base_cooldown": Decimal(5)
                    }
                },
                "garnet": {
                    "secondary": {
                        "base_damage": 0,
                        "base_cooldown": Decimal(3),
                        "effects": [ChargesAndResetsAbilityOnUse("special", charge_level=Decimal(3), probability=Decimal('0.5'))]
                    }
                },
                "emerald": {
                    "secondary": {
                        "effects_extend": [ChargesAbilityOnHit("primary", charge_amount=2, charge_level=Decimal('1.5'), max_charges=2)]
                    }
                }
            },
            "special": {
                "opal": {
                    "special": {
                        "base_damage": 300,
                        "base_cooldown": Decimal(4),
                        "effects": []
                    }
                },
                "sapphire": {
                    "special": {
                        "base_damage": 200,
                        "num_hits": 2
                    }
                },
                "ruby": {
                    "special": {
                        "effects_extend": [AppliesDebuffOnHit("Astral Swirl Burn", statuses.Burn, {'duration': Decimal(5)})]
                    }
                },
                "garnet": {
                    "special": {
                        "effects": [CooldownResetByUse("special", ["primary"], probability=Decimal('0.5'))]
                    }
                },
                "emerald": {
                    "special": {
                        "base_damage": 500,
                        "base_cooldown": Decimal(99)
                    }
                }
            },
            "defensive": {
                "opal": {
                    "defensive": {
                        "effects": [AppliesBuffOnUse("defensive", statuses.Haste, {'duration': Decimal(7)})]
                    }
                },
                "sapphire": {
                    "defensive": {
                        "effects": [AppliesBuffOnUse("defensive", statuses.BuffingField, {'duration': Decimal(3), 'buff': statuses.Vanish}, replace=True)]
                    }
                },
                "ruby": {
                    "defensive": {
                        "base_cooldown": Decimal(20),
                        "effects": [AppliesBuffOnUse("defensive", statuses.BuffingField, {'duration': Decimal(20), 'buff': statuses.Haste}, replace=True)]    
                    }
                },
                "garnet": {
                    "defensive": {
                        "effects": [CannotBeReset(), AppliesBuffOnUse("defensive", statuses.BuffingField, {'duration': Decimal(5), 'buff': statuses.RabbitLuck}, replace=True)]
                    }
                },
                "emerald": {
                    "defensive": {
                        "effects": [MultiplyDamage("ALL", Decimal('0.2'))]
                    }
                }
            }
        }
    }
}
