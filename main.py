#!/usr/bin/env python

import bf3stats
import cPickle
import jinja2
import os
import time
import datetime
import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from secrets import Secrets

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Constants
KIT_RECON = 'Recon'
KIT_ASSAULT = 'Assault'
KIT_SUPPORT = 'Support'
KIT_ENGINEER = 'Engineer'
KIT_GENERAL = 'General'

KITS = [KIT_ASSAULT, KIT_ENGINEER, KIT_RECON, KIT_SUPPORT, KIT_GENERAL]

AOA_MEMBERS = [
                'botono9',
                'dpg70',
                'benderisgr8',
                'V_V-RECKONER-V_V',
                'NY_Scumbag',
                'UnshavenCanuck',
                'oxsox',
                'TheHellRaisers3',
                'AVENTINUS78',
                'DecaturKing86',
                'Thorndoor',
                'Merkn_Muffley',
                'MatthewScars',
                'HELLeRaZoR',
                'Jung_at_Heart',
                'Deth_Lok',
                'becca0011',
                'todesengel1875',
                'ez_____ez_____ez',
                'Deaf_P0wnage',
                'couchkiller99',
                'squijjle',
                'Daddiode',
                'alankstiyo',
                ]


class Weapon(db.Model):
    """Model for Weapon"""
    weapon_id = db.StringProperty()
    weapon_name = db.StringProperty()
    weapon_description = db.StringProperty(multiline=True)
    weapon_kit = db.StringProperty()
    weapon_type = db.StringProperty()
    weapon_img = db.StringProperty()

class Player(db.Model):
    """Player Model"""
    player_name = db.StringProperty()
    player_stats = db.BlobProperty() # Pickled stats
    player_stats_updated = db.DateTimeProperty()
    player_active = db.BooleanProperty()

class Challenge(db.Model):
    """Challenge Model"""
    created = db.DateTimeProperty()
    weapons_primary = db.ListProperty(str)
    weapons_combination = db.ListProperty(str)

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
        template_values = {}
        
        template = jinja_environment.get_template('add_challenge.html')
        self.response.out.write(template.render(template_values))


class InitHandler(webapp2.RequestHandler):
    """docstring for InitHandler"""
    def get(self):
        template_values = {}
        mysecrets = Secrets()
        stats_obj = bf3stats.api(plattform='ps3', secret=mysecrets.bf3StatsKey, ident=mysecrets.bf3StatsIdent)

        # If weapon info is empty, fill it
        template_values['weapons_added'] = 'Weapons not added to datastore.'
        if not Weapon.all(keys_only=True).get():

            # Pull the information on all the Kits
            # Data looks like:
            # {'status': 'data', 'stats': {'kits': {'recon':{'name':'Recon', 'unlocks': [{'name':'','id':'', desc':'',}]}}}}
            kit_data = stats_obj.player('botono9', parts='clear,imgInfo,kits,kitsName,kitsInfo,kitsUnlocks')

            for k in kit_data['stats']['kits'].iterkeys():
                kit_name = kit_data['stats']['kits'][k]['name']
                for item in kit_data['stats']['kits'][k]['unlocks']:
                    Weapon(
                        weapon_id = item['id'],
                        weapon_name = item['name'],
                        weapon_description = item['desc'],
                        weapon_kit = kit_name,
                        weapon_type = item['type'], #weapon or kititem
                        weapon_img = item['img']).put()
            template_values['weapons_added'] = 'Weapons datastore filled!'

        # Update user info from Google Doc
        template_values['players_added'] = 'Players not added to datastore.'
        if not Player.all(keys_only=True).get():
            # Last updated date is in weapons_data['list'][member_name]['stats']['date_update']
            weapons_data = stats_obj.playerlist(AOA_MEMBERS, parts='clean,weapons')
            if weapons_data['status'] == 'ok':
                failed_members = weapons_data.get('failed', {})
                for member_name in weapons_data['list'].iterkeys():
                     Player(
                        player_name = member_name,
                        player_stats = cPickle.dumps(weapons_data['list'][member_name]['stats']['weapons']),
                        player_stats_updated = datetime.datetime.fromtimestamp(weapons_data['list'][member_name]['stats']['date_update']),
                        player_active = True).put()
            template_values['players_added'] = 'Players datastore filled!'
        template = jinja_environment.get_template('init.html')
        self.response.out.write(template.render(template_values))
        

app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/add', AddChallenge),
                                ('/init', InitHandler)],
                              debug=True)

