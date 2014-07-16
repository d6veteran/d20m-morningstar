# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# app.py serves the Morningstar application to end users on mobile devices.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import utils

from model import character
from model import party
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class BaseHandler(webapp.RequestHandler):
    def get_user(self):
        '''Returns a User object associated with a Google account.
        '''
        _trace = TRACE+'APIBase:: get_user() '
        logging.info(_trace)
        user = users.get_current_user()
        logging.info(_trace+'user = '+ str(user.email()))            
        return user    

class MainHandler(BaseHandler):
    def get(self):
        _trace = TRACE+'MainHandler.get() '
        logging.info(_trace)
        user = users.get_current_user()
        characters = models.Character.all().filter('user =', user).fetch(100)
        template_values = {
            'characters': characters,
            'user': user
        }
        generate(self, 'start.html', template_values)  

class CharacterHandler(BaseHandler):
    def get(self):
        _trace = TRACE+'CharacterHandler.get() '
        logging.info(_trace)        
        templates = models.PlayerCharacterTemplate.all().fetch(100) 
        user = users.get_current_user()
        template_values = {
            'templates': templates,
            'user': user
        }        
        generate(self, 'character_create.html', template_values)
        
    def post(self):  
        _trace = TRACE+'CharacterHandler.post() '
        logging.info(_trace)
        user = users.get_current_user()
        key = self.request.get('template')
        name = self.request.get('name')
        template = db.get(key)
        if template is not None:
            _player = character.createPlayerFromTemplate(template, name, user)
            lat = self.request.get('lat')
            lon = self.request.get('lon')
            location = db.GeoPt(utils.strToIntOrFloat(lat), 
                                utils.strToIntOrFloat(lon))
            
            _party = party.createJSONParty(_player, location)            
            
        self.redirect('/mobile/character/'+str(_player.key()))      

class CharacterSheetHandler(BaseHandler):
    def get(self, key):
        _trace = TRACE+'CharacterSheetHandler.get() '
        logging.info(_trace)        
        _character = db.get(key) 
        _player = character.getJSONPlayer(_character)
        _party = _character.party
        user = users.get_current_user()
        template_values = {
            'player': _player,
            'party': _party,
            'user': user
        }        
        generate(self, 'character_sheet.html', template_values)

class CharacterQuestHandler(BaseHandler):
    def get(self, key):
        _trace = TRACE+'CharacterQuestHandler.get() '
        logging.info(_trace)        
        _character = db.get(key) 
        _player = character.getJSONPlayer(_character)
        party_key = str(_character.party.key())
        user = users.get_current_user()
              
        template_values = {
            'player': _player,
            'party_key': party_key,
            'user': user
        }        
        generate(self, 'character_quest.html', template_values)

    def post(self, key):
        _trace = TRACE+'CharacterQuestHandler.post() '
        logging.info(_trace)
        logging.info(_trace+'key = '+key)
        #return {'foo': 123}
        self.redirect('/mobile/character/'+key+'/quest')

class CharacterAttackHandler(BaseHandler):
    def get(self, player_key, monster_party_key):
        _trace = TRACE+'CharacterAttackHandler.get() '
        logging.info(_trace)        
        _character = db.get(player_key) 
        _party = db.get(monster_party_key)
        monster_party = party.getJSONParty(_party)
        _player = character.getJSONPlayer(_character)        
        party_key = str(_character.party.key())
        user = users.get_current_user()
              
        template_values = {
            'player': _player,
            'monster_party': monster_party,
            'party_key': party_key,
            'user': user
        }        
        generate(self, 'character_attack.html', template_values)

    def post(self, key):
        _trace = TRACE+'CharacterQuestHandler.post() '
        logging.info(_trace)
        logging.info(_trace+'key = '+key)
        #return {'foo': 123}
        self.redirect('/mobile/character/'+key+'/quest')        

class LootHandler(BaseHandler):
    def get(self, player_party_key, monster_party_key):
        _trace = TRACE+'LootHandler.get() '
        logging.info(_trace)   
        keys = [player_party_key, monster_party_key]
        parties = db.get(keys)
        _party = None
        npc_party = None
        for p in parties:
            if p.class_name() == 'NonPlayerParty':
                npc_party = p
            elif p.class_name() == 'PlayerParty':
                _party = p
        
        party_key = str(_party.key())
        _player = character.getJSONPlayer(_party.leader)
        gold, entities = party.getGoldLoot(npc_party, _party)
        db.put(entities)
        user = users.get_current_user()
                        
        template_values = {
            'player': _player,
            'party_key': party_key,
            'gold': gold,
            'user': user
        }        
        generate(self, 'character_quest.html', template_values)
        
######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates/mobile', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))
                                            
##############################################################################
##############################################################################
application = webapp.WSGIApplication([('/mobile/character/create', 
                                       CharacterHandler),
                                      (r'/mobile/character/(.*)/quest', 
                                       CharacterQuestHandler),
                                      (r'/mobile/character/(.*)/attack/(.*)', 
                                       CharacterAttackHandler),                                       
                                      (r'/mobile/character/(.*)', 
                                       CharacterSheetHandler),
                                      (r'/mobile/party/(.*)/loot/(.*)',
                                       LootHandler), 
                                      (r'/mobile/.*', 
                                       MainHandler)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()