# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Admin.py defines the RequestHandlers and Methods for supporting admin level
# access to the game.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import seed
import utils

from model import character
from model import item
from model import loot
from model import monster
from model import power

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging
import urllib2

from django.utils import simplejson
from google.appengine.api import oauth
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class Admin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin.html', template_values)        

class InitAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_init.html', template_values)        

    def post(self, method):
        logging.info('################## InitAdmin:: post() ####################')
        if method == "races": 
            r = seed.seedRaces()
        elif method == "casts": 
            r = seed.seedCasts()
        elif method == "weapons": 
            r = item.seedWeapons()
        elif method == "armor": 
            r = item.seedArmor()            
        elif method == "attacks": 
            r = power.seedAttacks()
        elif method == "pc_templates":
            r = character.seedPlayerCharacterTemplates()                            
        elif method == "npcs": 
            r = seed.seedNPCs()
        elif method == "party": 
            r = seed.seedPlayerParty()     
        elif method == "ft_data": 
            r = seed.seedFTData()           
        elif method == "pins": 
            r = seed.seedPins()                                            
        #else: r = API404
        #return self.response.out.write(simplejson.dumps(r))
        self.redirect('/admin/init')  

class CastAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_cast.html', template_values)        

class RaceAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_race.html', template_values)

class ArmorAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_armor.html', template_values)

class WeaponAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_weapon.html', template_values)

class PowerAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_power.html', template_values)   

class CharacterAdmin(webapp.RequestHandler):
    def get(self, method):
        if method == "form":
            characters = models.PlayerCharacter.all().fetch(10)
            template_values = {
                'characters': characters
            }        
            generate(self, 'admin_character_form.html', template_values) 
        else:
            i = utils.strToInt(method)
            character = models.PlayerCharacter.get_by_id(i)    
            weapons = models.Weapon.all().fetch(100)
            powers = models.Power.all().fetch(100)                          
            template_values = {
                'character': character,
                'weapons': weapons,
                'powers': powers
            }        
            generate(self, 'admin_character.html', template_values)

class Test(webapp.RequestHandler):
    def get(self, method):
        _trace = TRACE+'Test:: get() '
        logging.info(_trace)
        if method == "start": 
            pc_templates = models.PlayerCharacterTemplate.all().fetch(100) 
            user = users.get_current_user()
            characters = models.Character.all().filter('user =', user).fetch(100)
            template_values = {
                'pc_templates': pc_templates,
                'characters': characters,
                'user': user
            }        
            generate(self, 'test/test_start.html', template_values)
            
        elif method == "quest":
            user = users.get_current_user()
            key = self.request.get('key')
            character = db.get(key)
            party = models.PlayerParty.all().filter('leader = ', character).get()
            template_values = {
                'party': party,
                'character': character,
                'user': user
            }        
            generate(self, 'test/test_quest.html', template_values) 
            
        elif method == "attack":
            user = users.get_current_user()
            key = self.request.get('key')
            character = db.get(key)
            items = db.get(character.items)
            powers = db.get(character.powers)
            party = models.PlayerParty.all().filter('leader = ', character).get()
            monster_party = models.NonPlayerParty.get_by_id(171)
            monsters = db.get(monster_party.monsters)
            template_values = {
                'party': party,
                'monster_party': monster_party,
                'monsters': monsters,
                'character': character,
                'items': items,
                'powers': powers,
                'user': user
            }        
            generate(self, 'test/test_attack.html', template_values)   
        
        elif method == "map": 
            battles = models.BattlePin.all().fetch(100)
            monsters = models.MonsterPartyPin.all().fetch(100)
            players = models.PlayerPartyPin.all().fetch(100) 
            battles_json = []
            monsters_json = []
            players_json = []
            for b in battles:
                lat, lon = utils.parseGeoPt(b.location)
                data = {'name': b.name,'lat': lat,'lon': lon}
                battles_json.append(data)
            for m in monsters:
                lat, lon = utils.parseGeoPt(m.location)
                data = {'name': m.name,'lat': lat,'lon': lon}
                monsters_json.append(data)  
            for p in players:
                lat, lon = utils.parseGeoPt(p.location)
                data = {'name': p.name,'lat': lat,'lon': lon}
                players_json.append(data)
              
            logging.info(_trace+'battles = '+simplejson.dumps(battles_json))
            logging.info(_trace+'monsters = '+simplejson.dumps(monsters_json))
            logging.info(_trace+'players = '+simplejson.dumps(players_json))
            template_values = {
                'players': simplejson.dumps(players_json),
                'monsters': simplejson.dumps(monsters_json),
                'battles': simplejson.dumps(battles_json)
            }        
            generate(self, 'test/test_map.html', template_values)

class Home(webapp.RequestHandler):  
    """Generates Morningstar home page.
    """
    def get(self):
        _trace = TRACE+'Home:: get() '
        logging.info(_trace)        
        battles = models.BattlePin.all().fetch(100)
        monsters = models.MonsterPartyPin.all().fetch(100)
        players = models.PlayerPartyPin.all().fetch(100) 
        battles_json = []
        monsters_json = []
        players_json = []
        for b in battles:
            lat, lon = utils.parseGeoPt(b.location)
            data = {'name': b.name,'lat': lat,'lon': lon}
            battles_json.append(data)
        for m in monsters:
            lat, lon = utils.parseGeoPt(m.location)
            data = {'name': m.name,'lat': lat,'lon': lon}
            monsters_json.append(data)  
        for p in players:
            lat, lon = utils.parseGeoPt(p.location)
            data = {'name': p.name,'lat': lat,'lon': lon}
            players_json.append(data)
              
        logging.info(_trace+'battles = '+simplejson.dumps(battles_json))
        logging.info(_trace+'monsters = '+simplejson.dumps(monsters_json))
        logging.info(_trace+'players = '+simplejson.dumps(players_json))
        template_values = {
            'players': simplejson.dumps(players_json),
            'monsters': simplejson.dumps(monsters_json),
            'battles': simplejson.dumps(battles_json)
        }        
        generate(self, 'main.html', template_values)
                     
######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))

##############################################################################
##############################################################################
application = webapp.WSGIApplication([('/admin/', Admin),
                                      ('/admin/init', InitAdmin),
                                      (r'/admin/init/(.*)', InitAdmin),
                                      ('/admin/cast', CastAdmin),
                                      ('/admin/race', RaceAdmin),
                                      ('/admin/armor', ArmorAdmin),
                                      ('/admin/weapon', WeaponAdmin),
                                      ('/admin/power', PowerAdmin),
                                      (r'/admin/character/(.*)', CharacterAdmin),
                                      (r'/admin/test/home', Home),
                                      (r'/admin/test/(.*)', Test)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()