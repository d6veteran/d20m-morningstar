# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# party.py defines the Data and Methods for providing access to Party 
# resources as well as actions Characters can invoke, as a member of a Party,
# on other Parties and their members.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import loot
import models
import rules

from model import pin
from settings import *
from utils import roll

############################# GAE IMPORTS ####################################
##############################################################################
import character
import logging
import monster
import time

from google.appengine.ext import db

######################## METHODS #############################################
##############################################################################
def getJSONParty(party):
    '''Returns a JSON representation of a Party.
    '''
    _trace = TRACE+'getJSONParty() '
    logging.info(_trace) 
    logging.info(_trace + 'player = ' + str(party.key()))
    json = {'key': str(party.key()), 'location': str(party.location),
            'log': party.log}

    if party.class_name() == 'PlayerParty':
        json['leader'] = str(party.leader.key())
        players_json = []
        players = db.get(party.players)
        for j in players:
            players_json.append(character.getJSONPlayer(j))
        json['players'] = players_json

    if party.class_name() == 'NonPlayerParty':
        if party.owner:
            json['owner'] = str(party.owner.nickname())
        # Active monsters
        monsters_json = []    
        monsters = db.get(party.monsters)
        for m in monsters:
            monsters_json.append(monster.getJSONMonster(m))
        json['monsters'] = monsters_json      
        # Dead monsters
        deadpool_json = []
        deadpool_monsters = db.get(party.deadpool)
        for d in deadpool_monsters:
            deadpool_json.append(monster.getJSONMonster(d))
        json['deadpool'] = deadpool_json
               
    return json
    
def updateJSONParty(party, *characters):
    '''Updates a Party with one or more Characters, and Returns a JSON 
    representation of the Party.
    '''
    _trace = TRACE+'updateJSONParty() '
    logging.info(_trace)
    
    return

def createJSONParty(leader, location, players=None):       
    """Creates a new Party for the Character.
    Returns: JSON representation of the Party.
    """
    _trace = TRACE+'createJSONParty() '
    logging.info(_trace)
    log = {'encounter_log': 
           {'total': 0, 'uniques': 0, 'start_time': time.time(),
            'last_encounter': {'time_since': 0, 'checks': 0}}}
            
    party = models.PlayerParty(location = location,
                               leader = leader,
                               players = [leader.key()],
                               log = log)

    db.put(party)
    
    _pin = pin.createPlayerPartyPin(location, 
                                    party, 
                                    leader)
                                    
    json = {'key': str(party.key()), 'pin_key': str(_pin.key()),   
            'leader_key': str(party.leader.key()), 'location': str(location), 
            'players': [str(party.leader.key())], 'log': str(log)}
                         
    return json

def getJSONQuest(party, player, geo_loc):
    '''Returns any events, parties, and traps found at the PlayerParties 
    location.
    '''
    quest = rules.rollEncounter(party, geo_loc)
    return quest 

def getJSONAttack(monster_party, monsters, attacker, attack):
    '''Returns results of each monster attacked, and entity List to be 
    updated.
    '''
    json_damage = []
    # For each monster attack, perform the attack
    for m in monsters:
        json_result, entities = rules.attackMonster(attacker, attack, m)
        json_damage.append(json_result)
        # If the monster is killed, update monster party and player xp
        if json_result['hp'] == 0:
            monster_party.monsters.remove(m.key())
            monster_party.deadpool.append(m.key())
            entities.append(monster_party)
            attacker.experience += m.experience
            entities.append(attacker)
                
    return json_damage, entities    

def getJSONLoot(monster_party, player_party):
    '''Returns results for Loot earned from defeated NonPlayerParty, and any
    entities to be updated.  
    '''
    _trace = TRACE + 'getJSONLoot() '
    logging.info(_trace)
    return   

def getGoldLoot(monster_party, player_party):
    '''Returns gold earned from defeated NonPlayerParty, and any entities to 
    be updated.  
    '''
    _trace = TRACE + 'getGoldLoot() '
    logging.info(_trace)
    entities = []
    level = monster_party.level
    gold = loot.goldLoot(level)
    _player = player_party.leader
    purse = _player.purse
    purse['gold'] += gold
    _player.purse = purse 
    entities.append(_player)
       
    # Update monster_party
    monster_party.looted = True
    entities.append(monster_party)   
     
    return gold, entities    
    
####################### DATA ################################################
##############################################################################
