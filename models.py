#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Aaron Murray on 2012-04-13.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

from google.appengine.ext import db

class Weapon(db.Model):
    """Model for Weapon"""
    weapon_id = db.StringProperty()
    weapon_name = db.StringProperty()
    weapon_description = db.StringProperty(multiline=True)
    weapon_kit = db.StringProperty()
    weapon_type = db.StringProperty()
    weapon_img = db.StringProperty()

class WeaponDupe(db.Model):
    """Model for Weapon"""
    weapon_id = db.StringProperty()
    weapon_name = db.StringProperty()
    weapon_description = db.StringProperty(multiline=True)
    weapon_kit = db.StringProperty()
    weapon_type = db.StringProperty()
    weapon_img = db.StringProperty()
    weapon_parent = db.ReferenceProperty(Weapon, collection_name="sub_weapons")

class Player(db.Model):
    """Player Model"""
    player_name = db.StringProperty()
    player_stats = db.BlobProperty() # Pickled stats
    player_stats_updated = db.DateTimeProperty()
    player_active = db.BooleanProperty()

class Challenge(db.Model):
    """Challenge Model"""
    created = db.DateTimeProperty()
    weapons = db.ListProperty(str)

class ChallengeMatch(db.Model):
    """MANY TO MANY ChallengeMatch"""
    player = db.ReferenceProperty(Player,
                                    required=True,
                                    collection_name='players')
    challenge = db.ReferenceProperty(Challenge,
                                    required=True,
                                    collection_name='challenges')
    starting_kills = db.IntegerProperty()
    current_kills = db.IntegerProperty()

def challenge_key(key_name=None):
    """docstring for challenge_key"""
    return db.Key.from_path('Challenge', key_name)

def delete_all_weapons():
    db.delete(Weapon.all())
    db.delete(WeaponDupe.all())
