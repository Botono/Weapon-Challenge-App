#!/usr/bin/env python

import webapp2
import bf3stats
import jinja2
import os
import time


from google.appengine.ext import db
from google.appengine.api import users
from secrets import Secrets

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Weapon(db.Model):
    """Model for Weapon"""
    weapon_id = db.StringProperty()
    weapon_name = db.StringProperty()
    weapon_description = db.StringProperty(multiline=True)
    weapon_kit = db.StringProperty()
    weapon_img = db.StringProperty()

class Player(db.Model):
    """Player Model"""
    player_name = db.StringProperty()

class Challenge(db.Model):
    """Challenge Model"""
    created = db.DateTimeProperty()
    weapon_id = db.ReferenceProperty(Weapon,
                                        required=True,
                                        collection_name='weapons')

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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(template_values))

class AddChallenge(webapp2.RequestHandler):
    """docstring for AddChallenge"""
    def get(self):
        self.response.out.write('ADD CHALLENGE')

class InitHandler(webapp2.RequestHandler):
    """docstring for InitHandler"""
    def get(self):
        template_values = {}
        # If weapon info is empty, fill it
        mysecrets = Secrets()
        stats_obj = bf3stats.api(plattform='ps3', secret=mysecrets.bf3StatsKey, ident=mysecrets.bf3StatsIdent)
        
        # Pull the information on all the Kits
        # Data looks like:
        # {'status': 'data', 'stats': {'kits': {KitKey:{'name':'Recon', 'unlocks': [{'name':'','id':'', desc':'',}]}}}}
        kit_data = stats_obj.player('botono9', parts='clear,imgInfo,kits,kitsName,kitsInfo,kitsUnlocks')
        # Update user info from Google Doc
        for k in kit_data['stats']['kits'].iterkeys():
            kit_name = kit_data['stats']['kits'][k]['name']
            for item in kit_data['stats']['kits'][k]['unlocks']:
                Weapon(
                    weapon_id = item['id'],
                    weapon_name = item['name'],
                    weapon_description = item['desc'],
                    weapon_kit = kit_name,
                    weapon_img = item['img']).put()
        
        template = jinja_environment.get_template('init.html')
        self.response.out.write(template.render(template_values))
        

app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/add', AddChallenge),
                                ('/init', InitHandler)],
                              debug=True)

