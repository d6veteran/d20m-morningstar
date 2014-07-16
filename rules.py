# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Rules.py defines the Methods for accessing game mechanics and rules.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import utils

from model import character
from model import item
from model import loot
from model import monster
from model import pin
from model import power
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import logging
import random
import time

from google.appengine.ext import db
from random import randrange

######################## METHODS #############################################
##############################################################################
    
def rollLoot(level=1): 
    '''Returns a randomly generated, level appropriate treasure package.  
    Result is a dictionary of loot items
    '''   
    return loot.loot(level)    
    
def attackMonster(attacker, attack, monster):
    '''Resolves an attack against a Monster. Returns the damage result as 
    a dictionary: {'damage': 10, 'keywords': ['Fire'], 'status': 'Hit'}, and
    Returns a List of entities to be updated.    
    '''
    _trace = TRACE+'rollAttack():: '
    logging.info(_trace)
    damage_keywords = attack.damage_keywords
    json = {'key': str(monster.key()), 'name': monster.name,
            'damage': 0, 'keywords': damage_keywords, 
            'status': 'Hit', 'hp': 0, 'xp': monster.experience}
    
    entities = [] 
    
    # Roll Attack, natural 20 is a Hit
    #attack_roll = utils.roll(20, 1)  
    attack_roll = 19  # FOR TESTING
    logging.info(_trace+'attack_roll = '+str(attack_roll))    
    
    if attack.class_name() == models.WPN:
        # get attack mod using proficiency and ability
        # if magic, add bonus
        # get defense value
        # compare values
        # hit?
        # assign damage
        # TODO:: if magic, check for keywords
        
        json_weapon = item.getJSONItem(models.WPN, attack)
        logging.info(_trace+'Attack = Item.Weapon')
        logging.info(_trace+'Weapon = '+str(json_weapon))
        if attack.magic == True: pass
        else: pass
        
        # Get Proficiency and Ability Mod, add to attack roll
        logging.info(_trace+'proficiency = '+str(attack.proficiency))
        logging.info(_trace+'attack_mod = '+str(attack.attack_mod))
        mod_attack_roll = attack_roll + attack.attack_mod + attack.proficiency
        logging.info(_trace+'mod_attack_roll = '+str(mod_attack_roll))    
            
        # Get Defense Score
        defense = 'AC'
        defense_score = monster.scores['defenses'][defense]['score']
        logging.info(_trace+'defense_score = '+str(defense_score))     
    
        # Evaluate Hit
        if mod_attack_roll < defense_score:
            logging.info(_trace+'Attack is a Miss!')
            json['status'] = 'Miss'

        # Roll Damage
        else:    
            logging.info(_trace+'Attack is a Hit!')
            damage_dice = attack.damage_dice 
            damage_die = attack.damage_die
            damage = 0
            if damage_die != 0:
                damage = utils.roll(damage_die, damage_dice)
            if attack.damage_mod:
                damage += damage_mod
            logging.info(_trace+'damage before defenses = '+str(damage))
    
            # Calculate Defenses
            immunities = monster.immunities
            resist =  monster.resist
            vulnerable = monster.vulnerable
            for d in damage_keywords:
                # No Damage if Monster has immunity
                if d in immunities:
                    json['status'] = 'Immune to '+d
                    return json        
        
                # Reduced Damage for resistence
                if resist is not None:
                    resist_keys = resist.keys()
                    if d in resist_keys:
                        mod = resist[d]
                        damage -= mod
                        json['status'] = 'Resists '+d
        
                # Increased Damage for vulnerability
                if vulnerable is not None:
                    vulnerable_keys = vulnerable.keys()
                    if d in vulnerable_keys:
                        mod = vulnerable[d]
                        damage += mod
                        json['status'] = 'Vulnerable to '+d                    
    
                # Damage cannot be less than 0
                if damage < 0:
                    damage = 0    
            
            # Update damage to monster, determine kill, assign experience
            hp = monster.hit_points['hp']
            hp -= damage
            if hp < 0:
                hp = 0
                monster.status = 'KIA'
                attacker.experience += monster.experience
                entities = [monster, attacker]
            
            monster.hit_points['hp'] = 0
                    
            json['hp'] = hp
            json['damage'] = damage     
                
    elif attack.class_name() == models.ATT:    
        # assign damage
        # Weapon damage?
        # -- get weapon
        # dice damage?
        # -- roll damage
        # Ability bonus to damage?
        # -- add to damage
        # damange keywords?
        # -- add/subtract
        json_attack = power.getJSONPower(models.ATT, attack)
        logging.info(_trace+'Attack = '+models.ATT)
        logging.info(_trace+'Attack = '+str(json_attack))
        
        # Get Attack Score
        logging.info(_trace+'attack_mod = '+str(attack.attack_mod))
        abil = attack.attack_ability
        logging.info(_trace+'attack ability = '+abil)
        ability_mod = attacker.scores['abilities'][abil]['mod']
        mod_attack_roll = attack_roll + attack.attack_mod + ability_mod
        logging.info(_trace+'mod_attack_roll = '+str(mod_attack_roll))    
         
        # Get Defense Score
        def_abil = attack.defense_ability
        defense_score = monster.scores['defenses'][def_abil]['score']
        logging.info(_trace+'defense ability = '+def_abil)        
        logging.info(_trace+'defense score = '+str(defense_score))         
    
        # Evaluate Hit
        if mod_attack_roll < defense_score:
            logging.info(_trace+'Attack is a Miss!')
            json['status'] = 'Miss'

        # Roll Damage
        else:    
            logging.info(_trace+'Attack is a Hit!')
            damage_dice = attack.damage_dice 
            damage_die = attack.damage_die
            ability = attack.damage_ability_type
            damage = 0
            # Check for mods and add Damage
            if damage_die != 0:
                damage_roll= utils.roll(damage_die, damage_dice)
                logging.info(_trace+'damage_roll = '+str(damage_roll))                  
                damage += damage_roll
            if ability:
                damage_mod = attacker.scores['abilities'][ability]['mod']
                damage += damage_mod
            if attack.damage_weapon_multiplier > 0:
                # TODO: currenty the associated weapon/implement is not passed
                # so a default is used ...
                damage += utils.roll(10, 1)
            logging.info(_trace+'damage before defenses = '+str(damage))  
    
            # Calculate Defenses
            immunities = monster.immunities
            resist =  monster.resist
            vulnerable = monster.vulnerable
            for d in damage_keywords:
                # No Damage if Monster has immunity
                if d in immunities:
                    json['status'] = 'Immune to '+d
                    return json        
        
                # Reduced Damage for resistence
                if resist is not None:
                    resist_keys = resist.keys()
                    if d in resist_keys:
                        mod = resist[d]
                        damage -= mod
                        json['status'] = 'Resists '+d
        
                # Increased Damage for vulnerability
                if vulnerable is not None:
                    vulnerable_keys = vulnerable.keys()
                    if d in vulnerable_keys:
                        mod = vulnerable[d]
                        damage += mod
                        json['status'] = 'Vulnerable to '+d                    
    
                # Damage cannot be less than 0
                if damage < 0:
                    damage = 0    
    
                json['damage'] = damage
    
    return json, entities
    
def rollEncounter(player_party, geo_pt):
    '''Creates a random monster encounter.  Returns a NonPlayerParty of
    monsters or None.  The chance of encountering monsters is based on the
    player_party's encounter log.
    ''' 
    _trace = TRACE+'rollEncounter():: '
    logging.info(_trace)
    logging.info(_trace+' player_party = '+str(player_party))    

    # Determine likelyhood of encounter ...
    '''
    {'encounter_log': {'total': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    '''
    log = player_party.log
    checks = log['encounter_log']['last_encounter']['checks']
    player_party.log['encounter_log']['last_encounter']['checks'] = checks + 1
    mod = checks*2
    r = utils.roll(100, 1)
    logging.info(_trace+'r = '+str(r))     
    
    if r > 97: unique = True
    else: unique = False
    r = r + mod 
    
    ### TEST ROLL - uncomment to test a specific roll
    r = 75
    ###
    
    # There is an Encounter :)
    if r >= 75:
        # Update the Encounter Log ...
        player_party.log['encounter_log']['total'] += 1
        last_encounter = {'time_since': time.time(), 'checks': 0}
        player_party.log['encounter_log']['last_encounter'] = last_encounter
        
        # Get number of PCs and the average level of the Party ...
        party_size = len(player_party.players)
        members = db.get(player_party.players)
        total = 0
        for m in members:
            total = total + m.level
        avg_level = total/party_size
        logging.info(_trace+'avg_level = '+str(avg_level))        
        monster_party = models.NonPlayerParty(location = geo_pt, 
                                              monsters = [],
                                              json = {'monsters': []},
                                              level = avg_level)
        
        # Get the appropriate Monster table for the Party level ...    
        monster_level = MONSTER_XP_LEVELS[avg_level]
        logging.info(_trace+'monster_level = '+str(monster_level))
        
        # Get XP target for the encounter based on party level and size ...
        party_xp = monster_level[models.STAN]*party_size   
        logging.info(_trace+'party_xp = '+str(party_xp))
        
        # Roll Monster Encounter template   
        if unique:
            r = 10
        else:    
            # Change die sides to exclude results from monster generator
            
            # Low level
            if avg_level < 3:
                r = utils.roll(8, 1) 
                
            # Higher level includes Solo encounters           
            else:
                r = utils.roll(9, 1) 
        
        logging.info(_trace+'r = '+str(r))
        
        ### TEST ROLL - uncomment to test a specific roll
        r = 1
        ###
        
        entities = []    
        label = None
        ######################################################################
        # Minions Minions Minions!
        if r == 1 or r == 2:
            logging.info(_trace+'Minions Minions Minions!')              

            #  Randomly adjust level to create more variety ...
            if avg_level > 3:
                r = utils.roll(5, 1)
                logging.info(_trace+'r = '+str(r)) 
                level_mod = 0
                if r == 1:
                    level_mod = +2
                if r == 2:
                    level_mod = +1
                if r == 3:
                    level_mod = 0
                if r == 4:
                    level_mod = -1
                if r == 5:
                    level_mod = -2
                
                avg_level += level_mod        
                logging.info(_trace+'new avg_level = '+avg_level) 
            
            # Get Minion XP and # of Minions for this level ...
            minion_xp = MONSTER_XP_LEVELS[avg_level][models.MIN]
            npc_party_size = party_xp/minion_xp
            logging.info(_trace+'npc_party_size = '+str(npc_party_size)) 
                        
            q = db.Query(models.NonPlayerCharacterTemplate, keys_only=True)                    
            q.filter('role = ', models.MIN)
            q.filter('challenge =', models.STAN)
            q.filter('level =', avg_level)
            q.filter('unique =', False)
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))  
            npc_key = npc_keys[r-1] # indexes start at 0
            npc = db.get(npc_key)
            for i in range(npc_party_size):
                m = monster.createMonsterFromTemplate(npc)
                monster_party.monsters.append(m.key())
                entities.append(m)
                
            label = str(npc_party_size) + ' ' + entities[0].name
            if npc_party_size > 1:
                label += 's'

                
        ######################################################################
        # There's one for everyone.                
        elif r == 3 or r == 4:  
            logging.info(_trace+'There\'s one for everyone!')  
            logging.info(_trace+'monster_level = '+str(monster_level[models.STAN]))
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.STAN)
            q.filter('experience =', monster_level[models.STAN])
            q.filter('level =', avg_level)
            q.filter('unique =', False)    
            logging.info(_trace+'query = '+str(q))             
            npc_keys = q.fetch(100)         
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r-1]
            npc = db.get(npc_key)
            monster_party_size = party_size
            for i in str(monster_party_size):
                m = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
                entities.append(m)            

        ######################################################################        
        # Minions plus Mini-boss - oh noze!   
        elif r == 5 or r == 6:
            logging.info(_trace+'Minions + Mini-boss!')                
            boss_level = avg_level + 2        
            logging.info(_trace+'boss_level = '+boss_level)

            # Get Mini-boss
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.LEAD)
            q.filter('level =', boss_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))                
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))              
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            elite = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
            entities.append(elite)            
            
            # Get Minions
            race = elite.race
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge =', models.STAN)
            q.filter('level =', avg_level)
            q.filter('unique =', False)    
            q.filter('race =', race)                      
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r]
            npc = db.get(npc_key)

            # Get Minion XP and # of Minions for this level ...
            minion_xp = MONSTER_XP_LEVELS[avg_level][models.MIN]
            npc_party_size = party_xp/minion_xp
            logging.info(_trace+'npc_party_size = '+str(npc_party_size))

            for i in str(npc_party_size):
                m = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
                entities.append(m)
                        
        ######################################################################
        # Dungeon Master party.            
        elif r == 7 or r == 8:
            logging.info(_trace+'You made the DM angry!') 
            # Return a set monster party  ...

        ######################################################################        
        # Solo boss - uh-oh.                        
        elif r == 9:  
            logging.info(_trace+'Solo boss - uh-oh!')              
            #  Randomly adjust level to create more variety ...
            if avg_level > 1:
                r = utils.roll(3, 1)
                level_mod = 0  
                if r == 1:
                    level_mod = -1
                if r == 2:
                    level_mod = 0
                if r == 3:
                    level_mod = 1             
                avg_level += level_mod        
                logging.info(_trace+'new avg_level = '+avg_level)
                                
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.SOLO)
            q.filter('level =', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = models.Monster(npc = npc_key,
                                  json = character.getJSONNonPlayer(npc))
                                
            entities.append(solo)  
     


            
        ######################################################################        
        elif r == 10: # Unique NPC.
            logging.info(_trace+'Unique NPC')
            player_party.log['encounters']['uniques'] += 1            
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('level =', avg_level)
            q.filter('unique =', True)            
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = models.Monster(npc = npc_key,
                                  json = character.getJSONNonPlayer(npc))
                            
            entities.append(solo)
            
            # More than 1 Player? Throw in some Minions and make it a Party!
            if party_size > 1:
                q = db.Query(models.NonPlayerCharacter, keys_only=True)
                q.filter('role =', models.MIN)
                q.filter('challenge =', models.STAN)
                q.filter('level =', avg_level)
                q.filter('unique =', False)            
                npc_keys = q.fetch(100)
                r = utils.roll(len(npc_keys), 1)
                npc_key = npc_keys[r]
                npc = db.get(npc_key)
                minion_party_size = party_size*4
                for i in minion_party_size:
                    m = models.Monster(npc = npc_key,
                                       json = character.getJSONNonPlayer(npc))

                    entities.append(m)                    

    else:
        return None            
    
    db.put(entities) # IDs assigned

    # Need a new loop to get monster JSON after IDs are created ... 
    for e in entities:
        monster_json = monster.getJSONMonsterLite(e)
        monster_party.json['monsters'].append(monster_json)

    parties = [player_party, monster_party]        
    db.put(parties)
    
    # Create pin
    monster_loc = spawnLocation(player_party.location)    
    _pin = pin.createMonsterPartyPin(monster_loc, monster_party, entities)
    monster_party.json['pin_key'] = str(_pin.key())
    monster_party.json['location'] = str(monster_loc)
    monster_party.json['label'] = label

    return monster_party    

def logBattle(location, loot, *characters):
    '''Stores a summary of a battle. 
    '''
    return True
    
def spawnLocation(location, meters=60):
    """Creates a new location within random meters of provided location.
    Returns: a new location.
    """   
    _trace=TRACE+"spawnLocation() "
    logging.info(_trace)
    lat, lon = utils.parseGeoPt(location)
    logging.info(_trace+'lat = '+lat)
    logging.info(_trace+'lon = '+lon)
    
    # Randomly determine distance of new lat/lon
    ran_lat_meters = utils.roll(meters, 1)
    ran_lon_meters = utils.roll(meters, 1)
    logging.info(_trace+'ran_lat_meters = '+str(ran_lat_meters))
    logging.info(_trace+'ran_lon_meters = '+str(ran_lon_meters))
        
    lat_meters = ran_lat_meters*.00001
    lon_meters = ran_lon_meters*.00001
    logging.info(_trace+'lat_meters = '+str(lat_meters))
    logging.info(_trace+'lon_meters = '+str(lon_meters))

    # Randomly determine direction of new lat/lon
    pos_lat_vector = random.choice([True, False])
    pos_lon_vector = random.choice([True, False])
    logging.info(_trace+'pos_lat_vector = '+str(pos_lat_vector))
    logging.info(_trace+'pos_lon_vector = '+str(pos_lon_vector))
        
    lat = utils.strToIntOrFloat(lat)
    lon = utils.strToIntOrFloat(lon)
    new_lat = lat
    new_lon = lon
    if pos_lat_vector == False:
        new_lat = lat - lat_meters  
        logging.info(_trace+'False new_lat = '+str(new_lat))
    
    else:
        new_lat = lat + lat_meters              
        logging.info(_trace+'True new_lat = '+str(new_lat))
        
    if pos_lon_vector == False:
        new_lon = lon - lon_meters
        logging.info(_trace+'False new_lon = '+str(new_lon))    
    
    else:
        new_lon = lon + lon_meters
        logging.info(_trace+'True new_lon = '+str(new_lon))
                        
    new_location = db.GeoPt(str(new_lat), str(new_lon))
    return new_location

######################## DATA ################################################
##############################################################################    

MONSTER_XP_LEVELS = [
    None,
    {models.STAN: 100, models.MIN: 25, models.ELIT: 200, models.SOLO: 500},
    {models.STAN: 125, models.MIN: 31, models.ELIT: 250, models.SOLO: 625},
    {models.STAN: 150, models.MIN: 38, models.ELIT: 300, models.SOLO: 750},
    {models.STAN: 175, models.MIN: 44, models.ELIT: 350, models.SOLO: 875},
    {models.STAN: 200, models.MIN: 50, models.ELIT: 400, models.SOLO: 1000},
    {models.STAN: 250, models.MIN: 63, models.ELIT: 500, models.SOLO: 1250},
    {models.STAN: 300, models.MIN: 75, models.ELIT: 600, models.SOLO: 1500},
    {models.STAN: 350, models.MIN: 88, models.ELIT: 700, models.SOLO: 1750},
    {models.STAN: 400, models.MIN: 100, models.ELIT: 800, models.SOLO: 2000},
    {models.STAN: 500, models.MIN: 125, models.ELIT: 1000, models.SOLO: 2500},
    {models.STAN: 600, models.MIN: 150, models.ELIT: 1200, models.SOLO: 3000},
    {models.STAN: 700, models.MIN: 175, models.ELIT: 1400, models.SOLO: 3500},
    {models.STAN: 800, models.MIN: 200, models.ELIT: 1600, models.SOLO: 4000},
    {models.STAN: 1000, models.MIN: 250, models.ELIT: 2000, models.SOLO: 5000},
    {models.STAN: 1200, models.MIN: 300, models.ELIT: 2400, models.SOLO: 6000},
    {models.STAN: 1400, models.MIN: 350, models.ELIT: 2800, models.SOLO: 7000},
    {models.STAN: 1600, models.MIN: 400, models.ELIT: 3200, models.SOLO: 8000},
    {models.STAN: 2000, models.MIN: 500, models.ELIT: 4000, models.SOLO: 10000},
    {models.STAN: 2400, models.MIN: 600, models.ELIT: 4800, models.SOLO: 12000},
    {models.STAN: 2800, models.MIN: 700, models.ELIT: 5600, models.SOLO: 14000},
    {models.STAN: 3200, models.MIN: 800, models.ELIT: 6400, models.SOLO: 16000},
    {models.STAN: 4150, models.MIN: 1038, models.ELIT: 8300, models.SOLO: 20750},
    {models.STAN: 5100, models.MIN: 1275, models.ELIT: 10200, models.SOLO: 25500},
    {models.STAN: 6050, models.MIN: 1513, models.ELIT: 12100, models.SOLO: 30250},
    {models.STAN: 7000, models.MIN: 1750, models.ELIT: 14000, models.SOLO: 35000},
    {models.STAN: 9000, models.MIN: 2250, models.ELIT: 18000, models.SOLO: 45000},
    {models.STAN: 11000, models.MIN: 2750, models.ELIT: 22000, models.SOLO: 55000},
    {models.STAN: 13000, models.MIN: 3250, models.ELIT: 26000, models.SOLO: 65000}]
