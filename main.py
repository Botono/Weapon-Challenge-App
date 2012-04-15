#!/usr/bin/env python

import bf3stats
import cPickle
import jinja2
import os
import time
import datetime
import webapp2
import models # my models


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


class FixPistolsHandler(webapp2.RequestHandler):
    """docstring for FixPistolsHandler"""
    def get(self):
        template_values = {}
        main_pistols = {'pM1911': ['pM1911S', 'pM1911L'],
                        'pG17': ['pG17S'],
                        'pg18': ['pg18S'],
                        'pM9': ['pM9F', 'pM9S'],
                        'pMP443': ['pMP443L', 'pMP443S'],
                        'pTaur': ['pTaurS'],}
        template_values['main_pistols'] = main_pistols
        template_values['sub_pistols'] = []
        for main_pistol_id in main_pistols.iterkeys():
            main_pistol = models.Weapon.gql("WHERE weapon_id = :1", main_pistol_id).get()
            sub_pistols = main_pistols[main_pistol_id]
            for sub_pistol_id in sub_pistols:
                template_values['sub_pistols'].append(sub_pistol_id)
                sub_pistol = models.Weapon.gql("WHERE weapon_id = :1", sub_pistol_id).get()
                sub_pistol_data = {}
                sub_pistol_data['weapon_id'] = sub_pistol.weapon_id
                sub_pistol_data['weapon_name'] = sub_pistol.weapon_name
                sub_pistol_data['weapon_description'] = sub_pistol.weapon_description
                sub_pistol_data['weapon_kit'] = sub_pistol.weapon_kit
                sub_pistol_data['weapon_type'] = sub_pistol.weapon_type
                sub_pistol_data['weapon_img'] = sub_pistol.weapon_img
                sub_pistol.delete()
                new_sub_pistol = models.WeaponDupe(
                        weapon_id = sub_pistol_data['weapon_id'],
                        weapon_name = sub_pistol_data['weapon_name'],
                        weapon_description = sub_pistol_data['weapon_description'],
                        weapon_kit = sub_pistol_data['weapon_kit'],
                        weapon_type = sub_pistol_data['weapon_type'], #weapon or kititem
                        weapon_img = sub_pistol_data['weapon_img'],
                        weapon_parent = main_pistol).put()
        template = jinja_environment.get_template('fixpistols.html')
        self.response.out.write(template.render(template_values))

class InitHandler(webapp2.RequestHandler):
    """docstring for InitHandler"""
    def get(self):
        template_values = {}
        mysecrets = Secrets()
        stats_obj = bf3stats.api(plattform='ps3', secret=mysecrets.bf3StatsKey, ident=mysecrets.bf3StatsIdent)

        # If weapon info is empty, fill it
        template_values['weapons_added'] = 'Weapons not added to datastore.'
        if not models.Weapon.all(keys_only=True).get():

            # Pull the information on all the Kits
            # Data looks like:
            # {'status': 'data', 'stats': {'kits': {'recon':{'name':'Recon', 'unlocks': [{'name':'','id':'', desc':'',}]}}}}
            kit_data = stats_obj.player('botono9', parts='clear,imgInfo,kits,kitsName,kitsInfo,kitsUnlocks')

            for k in kit_data['stats']['kits'].iterkeys():
                kit_name = kit_data['stats']['kits'][k]['name']
                for item in kit_data['stats']['kits'][k]['unlocks']:
                    models.Weapon(
                        weapon_id = item['id'],
                        weapon_name = item['name'],
                        weapon_description = item['desc'],
                        weapon_kit = kit_name,
                        weapon_type = item['type'], #weapon or kititem
                        weapon_img = item['img']).put()
                # HACK IT!
            models.Weapon(
                weapon_id = 'pM9',
                weapon_name = 'M9',
                weapon_description = """Formally known as Pistol, Semiautomatic, 9mm, M9, the M9 was selected as the primary sidearm of the entire United States military in 1985. Developed in Italy, the M9 was selected in a series of often disputed trials, only narrowly beating out other contenders, because of its high quality and low price. The M9 is the primary sidearm of the USMC.""",
                weapon_kit = 'General',
                weapon_type = 'weapon', #weapon or kititem
                weapon_img = 'weapons/m9.png').put()
            template_values['weapons_added'] = 'Weapons datastore filled!'

        # Update user info from Google Doc
        template_values['players_added'] = 'Players not added to datastore.'
        if not models.Player.all(keys_only=True).get():
            # Last updated date is in weapons_data['list'][member_name]['stats']['date_update']
            weapons_data = stats_obj.playerlist(AOA_MEMBERS, parts='clean,weapons')
            if weapons_data['status'] == 'ok':
                failed_members = weapons_data.get('failed', {})
                counter = 0
                for member_name in weapons_data['list'].iterkeys():
                    models.Player(
                        player_name = member_name,
                        player_stats = cPickle.dumps(weapons_data['list'][member_name]['stats']['weapons']),
                        player_stats_updated = datetime.datetime.fromtimestamp(weapons_data['list'][member_name]['stats']['date_update']),
                        player_active = True).put()
            template_values['players_added'] = 'Players datastore filled!'
        template = jinja_environment.get_template('init.html')
        self.response.out.write(template.render(template_values))

class DeleteWeaponsHandler(webapp2.RequestHandler):
    """docstring for DeleteWeaponsHandler"""
    def get(self):
        template_values = {}
        # EVERYONE!!!!!
        models.delete_all_weapons()
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/add', AddChallenge),
                                ('/init', InitHandler),
                                ('/fixpistols', FixPistolsHandler),
                                ('/deleteweapons', DeleteWeaponsHandler)],
                              debug=True)

