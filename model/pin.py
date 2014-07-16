# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# pin.py provides CRUD for Pin models.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models

from utils import roll
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from google.appengine.ext import db
from random import choice

############################# CONSTANTS ######################################
##############################################################################

######################## METHODS #############################################
##############################################################################
def createBattlePin(location, players, monsters, log):
    """Creates a new BattlePin.  
    Returns: a new BattlePin.        
    """
    _trace = TRACE+"setBattlePin() "
    logging.info(_trace)
    pin = models.BattlePin(location = location,
                           players = players,
                           monsters = monsters,
                           log = log)
    db.put(pin)                                
    return pin

def updateBattlePin(pin, log, players=None):
    """Updates the log of a BattlePin, and any new players added to the 
    battle.  
    Returns: the BattlePin.        
    """
    _trace = TRACE+"updateBattlePin() "
    logging.info(_trace)
    # TODO - UPDATE LOG
    #pin.log = log
 
    db.put(pin)     
    return pin    

def createMonsterPartyPin(location, party, monsters=None):
    """Creates a new MonsterPartyPin.  If no Monster Entities are passed, 
    the party will be derefrenced to load monsters.
    Returns: a new MonsterPartyPin.        
    """
    _trace = TRACE+"setMonsterPartyPin() "
    logging.info(_trace)
    if monsters is None:
        monsters = db.get(party.monsters)
    log = {'monsters': []}
    for m in monsters:
        monster = {'key': str(m.key()), 'name': m.name, 'level': m.level}
        log['monsters'].append(monster)
    
    pin = models.MonsterPartyPin(location = location,
                                 monster_party = party,
                                 monsters = monsters,
                                 log = log)

    db.put(pin)      
    return pin

def createPlayerPartyPin(location, party, leader, players=None):
    """Creates a new PlayerPartyPin.  
    Returns: a new PlayerPartyPin.        
    """
    _trace = TRACE+"setPlayerPartyPin() "
    logging.info(_trace)
    _leader = {'key': str(leader.key()), 'name': leader.name, 
               'level': leader.level}
               
    log = {'players': [], 'leader': _leader}    
    if players is not None:
        for p in players:
            player = {'key': str(p.key()), 'name': p.name, 'level': p.level}
            log['players'].append(player)
    
    pin = models.PlayerPartyPin(location = location,
                                players = players,
                                player_party = party,
                                log = log)

    db.put(pin)      
    return pin

def createKillPin(location, players, monsters, log):
    """Creates a new KillPin.  
    Returns: a new KillPin.        
    """
    _trace = TRACE+"setKillPin() "
    logging.info(_trace)
    pin = models.KillPin(location = location,
                         player = player,
                         log = log)
                                    
    db.put(pin)  
    return pin  

    