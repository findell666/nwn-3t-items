from email.mime import base
import sys
import os
import io
import numpy as np

from pynwn.player_character import PlayerCharacter
from pynwn.item import ItemInstance
from pynwn.item import Item
from pynwn.item import ItemProperty
from pynwn.resource import DirectoryContainer
from pynwn.file.gff import GffInstance
from pynwn.file.tlk import Tlk

#my items, all items onglets?
#item sheet, last seen by (autorisation)
#tiers of items
#whishlist
#custom2DA files, select default peristent world.
#server normal, server EE, bandeau différent
#auth
#sauvegarde des persos, et des versions ?
#correspondance avec les traductions des propriétés ! formatage !

#commencer avec 3T
#00 mise en base, créer json coté pytohn
#0 connection, choix normal ou EE, ou serveur ?
#1 base PC, item, liste de mes items, alimentation de la base globale

dialog = os.path.join("./resources/tlk/", 'dialog.tlk')    
tlk = Tlk(open(dialog, 'rb'))

#chelou ces 3
#1 - 9, 22, 45, 56 - 59 Enhancement, Attack, AC, ... : ("./resources/2da/iprp_bonuscost.2da", 1, 2)
#4, 8, 18, 58, 64 RACIAL_TYPE : ("./resources/2da/racialtypes.2da", 3, 1)
#5, 9, 19, 59, 65 SPECIFIC_ALIGNMENT : ("./resources/2da/iprp_alignment.2da", 1, 2)

ITEMPROPDEF = "./resources/2da/itempropdef.2da"
BASEITEMS = "./resources/2da/baseitems.2da"

#TUPLES : File path / Name pos / Label pos
ALLS = ("./resources/2da/iprp_bonuscost.2da", 1, 2)
SR_COST = ("./resources/2da/iprp_srcost.2da", 1, 2) # SR
RES_COST = ("./resources/2da/iprp_resistcost.2da", 1, 2) # DR
SKILL_COST = ("./resources/2da/iprp_skillcost.2da", 1, 2) # skills cost
RED_COST = ("./resources/2da/iprp_redcost.2da", 1, 2) #bags
WEIGHT_COST = ("./resources/2da/iprp_weightcost.2da", 1, 2) 
CHARGE_COST = ("./resources/2da/iprp_chargecost.2da", 1, 2)
MONST_COST = ("./resources/2da/iprp_monstcost.2da", 1, 2)
DAMAGE_COST = ("./resources/2da/iprp_damagecost.2da", 1, 2)
SPECIFIC_ALIGNMENT = ("./resources/2da/iprp_alignment.2da", 1, 2)
RACIAL_TYPE = ("./resources/2da/racialtypes.2da", 3, 1)
AC_TYPE = ("./resources/2da/iprp_acmodtype.2da", 1, 2)
ABILITY = ("./resources/2da/iprp_abilities.2da", 1, 2)
ALIGNMENT_GROUP = ("./resources/2da/iprp_aligngrp.2da", 1, 2)
BONUS_FEAT = ("./resources/2da/iprp_feats.2da", 1, 2)
CAST_SPELL = ("./resources/2da/iprp_spells.2da", 2, 1)
CLASS = ("./resources/2da/classes.2da", 2, 1)
DAMAGE_TYPE = ("./resources/2da/iprp_damagetype.2da", 1, 2)
EXTRA_MELEE_DAMAGE_TYPE = ("./resources/2da/iprp_combatdam.2da", 1, 2)
IMMUNITY = ("./resources/2da/iprp_immunity.2da", 1, 2)
IMMU_COST = ("./resources/2da/iprp_immuncost.2da", 1, 2)
IMMUNITY_SPELL_SCHOOL = ("./resources/2da/spellschools.2da", 3, 1)
ON_HIT_COST = ("./resources/2da/iprp_onhitcost.2da", 1, 2)
ON_HIT_DUR = ("./resources/2da/iprp_onhitdur.2da", 1, 2)
ON_HIT = ("./resources/2da/iprp_onhit.2da", 1, 2)
ON_HIT_CAST_SPELL = ("./resources/2da/iprp_onhitspell.2da", 2, 1)
ON_MONSTER_HIT = ("./resources/2da/iprp_monsterhit.2da", 1, 2)
POISON_ON_MONSTER_HIT = ("./resources/2da/poison.2da", 2, 1)
SAVING_THROW_BONUS = ("./resources/2da/iprp_saveelement.2da", 1, 2)
SAVING_THROW_BONUS_SPECIFIC = ("./resources/2da/iprp_savingthrow.2da", 1, 2)
SKILL = ("./resources/2da/skills.2da", 2, 1)
SPECIAL_WALK = ("./resources/2da/iprp_walk.2da", 1, 2)
TRAP = ("./resources/2da/iprp_traps.2da", 1, 2)
UNLIMITED_AMMUNITION = ("./resources/2da/iprp_ammotype.2da", 1, 2)
VISUAL_EFFECT = ("./resources/2da/iprp_visualfx.2da", 2, 1)

# make a 2DA for that ?
CATEGORIES = ["none", "melee", "ranged", "shield", "armor", "helmet", "ammo", "thrown", "staves", "potion", "scroll", "thieves' tools", "misc",
"wands", "rods", "traps", "misc unequippable", "container", "??", "healers", "torches"]
def getBaseItemName(baseItem):
    return getValueFrom2DA(BASEITEMS, 1, 3, baseItem, True)

def getBaseItemList():
    baseItems = []

    for x in range (0, 112):
        name = getBaseItemName(x)
        category = getValueFrom2DA(BASEITEMS, 27, 27, x, False)
        # baseCost = getValueFrom2DA(BASEITEMS, 28, 28, x, False)
        
        if("****" == name or "*" == name or "Bad Strref" == name 
        or category == "****" or category == "*"):
        # or baseCost == "****" or baseCost == "*"):
            continue
        baseItems.append({"code":x , "name" : name, "category": int(category)})     
    return baseItems

def getBaseItemsCategories():    
    baseItemsList = getBaseItemList()
    baseItemsCategories = np.empty(21, dtype=object) 
    for x in range (len(baseItemsList)):        
        category = baseItemsList[x].get("category")
        if(None == baseItemsCategories[category]):
            baseItemsCategories[category] = []
        baseItemsCategories[category].append(baseItemsList[x])

    categories = []
    for x in range (len(baseItemsCategories)):
        if(None != baseItemsCategories[x]):
            dic = {"category" : x, "name": CATEGORIES[x], "elts": baseItemsCategories[x], "len": len(baseItemsCategories[x])}
            categories.append(dic)
    return categories        

def getValueFrom2DA(f, pos1, pos2, value, useResRef=True):
    file = open(f)
    all_lines = file.readlines()
    file.close()
    #print(str(value)  + " : " + f)
    if len(all_lines) < value+3:
        return value
    
    line = all_lines[value+3] #start 4th line
    array = line.split()
    if array[pos1] != "****" and useResRef: 
        return tlk.__getitem__(int(array[pos1]))
    return array[pos2]

def getPropertyName2DAValue(prop):
    return getValueFrom2DA(ITEMPROPDEF, 7, 7, prop)

#from LETO, I didnt find the info in nwn
def getSubType2DAFile(prop):
    switcher = {
        28: CLASS, #AC_TYPE,
        0 : ABILITY, #, KEEN TOut ça
        27: CLASS, #ABILITY, 
        2 : ABILITY,
        7 : ALIGNMENT_GROUP,
        17: ALIGNMENT_GROUP,
        57: ALIGNMENT_GROUP,
        62: ALIGNMENT_GROUP,
        12 : BONUS_FEAT,
        15 : CAST_SPELL,
        13 : CLASS,
        63 : CLASS,
        10 : DAMAGE_TYPE,        
        16 : DAMAGE_TYPE,
        20 : DAMAGE_TYPE,
        23 : DAMAGE_TYPE,
        24 : DAMAGE_TYPE,
        3 : EXTRA_MELEE_DAMAGE_TYPE,
        33 : EXTRA_MELEE_DAMAGE_TYPE, 
        34 : EXTRA_MELEE_DAMAGE_TYPE,
        37 : IMMUNITY,
        54 : IMMUNITY_SPELL_SCHOOL,
        48 : ON_HIT,
        82 : ON_HIT_CAST_SPELL,
        72 : ON_MONSTER_HIT,
        21 : POISON_ON_MONSTER_HIT,
        4 : RACIAL_TYPE,
        8 : RACIAL_TYPE,
        18 : RACIAL_TYPE,
        58 : RACIAL_TYPE,
        64 : RACIAL_TYPE, 
        40 : SAVING_THROW_BONUS,
        49 : SAVING_THROW_BONUS,
        41 : SAVING_THROW_BONUS_SPECIFIC,
        50 : SAVING_THROW_BONUS_SPECIFIC,
        29 : SKILL, 
        52 : SKILL,
        79 : SPECIAL_WALK,
        5 : SPECIFIC_ALIGNMENT,
        9 : SPECIFIC_ALIGNMENT,
        19 : SPECIFIC_ALIGNMENT,
        59 : SPECIFIC_ALIGNMENT,
        65 : SPECIFIC_ALIGNMENT ,
        70 : TRAP,
        61 : UNLIMITED_AMMUNITION,
        83 : VISUAL_EFFECT,
        #1 - 9, 22, 45, 56 - 59 Enhancement, Attack, AC, ...         
    }
    return switcher.get(prop, None)
    
def getCostValue2DAFile(prop, sub):
    #weapon dmg
    if prop == 16: # and (sub in (12, 11, 9):
        return (DAMAGE_COST, False)
    #uses
    if prop == 15:
        return (CHARGE_COST, True)
    #reduction weight bags
    if prop == 32:
        return (RED_COST, True)
    # +1 to +12
    if prop in (0, 1, 6, 51, 40, 41, 45, 56, 67):
        return (ALLS, True)
    #DR        
    if prop == 23:
        return (RES_COST, True)
    #skill
    if prop == 52:
        return (SKILL_COST, True)
    #spell resistance
    if prop == 39:
        return (SR_COST, True)
    #racial group
    if prop == 48 and sub == 21:
        return (ON_HIT_COST, True)
    #on hit dmg
    if prop == 48 and sub == 25:
        return (ON_HIT_COST, True)
    #on hit dmg
    if prop == 48 and sub == 17:
        return (ON_HIT_COST, True)                
    if prop == 11:
        return (WEIGHT_COST, True)
    #immunity bonus        
    if prop == 20:
        return (IMMU_COST, True)        
    return None  
    
def getParam12DAFile(prop, sub):
    #racial group
    if prop == 48 and sub == 21:
        return (ON_HIT_DUR, True)

def getParam1Value2DAFile(prop, sub, param):
    #racial group
    if prop == 48 and sub == 21 and param == 5:
        return (RACIAL_TYPE, True)        

def getSubType2DAResRef(prop, sub):
    Dda = getSubType2DAFile(int(prop))
    if Dda != None:
        return getValueFrom2DA(Dda[0], Dda[1], Dda[2], sub)
    if sub == 0 or sub == 65535:
        return ""
    return sub   
    
def getCostValue2DAResRef(prop, sub, cost):
    res = getCostValue2DAFile(int(prop), int(sub))
    if res != None:
        Dda = res[0]
        useResRef = res[1]    
        return getValueFrom2DA(Dda[0], Dda[1], Dda[2], cost, useResRef)
    if cost == 0:
        return ""
    return cost
    
def getParam12DAResRef(prop, sub, param1):
    res = getParam12DAFile(int(prop), int(sub))
    if res != None:
        Dda = res[0]
        useResRef = res[1]    
        return getValueFrom2DA(Dda[0], Dda[1], Dda[2], param1, useResRef)
    if param1 == 0:
        return ""
    return param1
    
def getParam1Value2DAResRef(prop, sub, param1, param1Value):
    res = getParam1Value2DAFile(int(prop), int(sub), int(param1))
    if res != None:
        Dda = res[0]
        useResRef = res[1]    
        return getValueFrom2DA(Dda[0], Dda[1], Dda[2], param1Value, useResRef)
    if param1Value == 0:
        return ""
    return param1Value              

def printItem(item, tlk=None):
    string = "-----------------------------------------------------------------------------<br />"
    #essayer de récuper le resref ici quand None pour aller chercher la string dans le tlk
    if None != item.get_name(0) and "None" != item.get_name(0):
        string += "NAME : " + str(item.get_name(0)) + "<br />"
    else:
        if None == tlk:
            string += "NAME : " + str(item.get_name()) + "<br />"
        else:
            string += "NAME : " + str(tlk.__getitem__(item.get_name())) + "<br />"
    string +="DESC ID : " + str(item.get_description_id(0)) + "<br />"
    string += "DISPLAY NAME : " + str(item.display_name) + "<br />"
    string += "BASEITEM : " + str(item.base_type) + "<br />"
    string +="TAG : " + str(item.tag) + "<br />"
    return string

def printProperty(prop):
    propn = prop.gff["PropertyName"]
    sub = prop.gff["Subtype"]
    cost = prop.gff["CostValue"]
    return str(getPropertyName2DAValue(propn)) + " " + str(getSubType2DAResRef(propn, sub)) + " " + str(getCostValue2DAResRef(propn, sub, cost)) + "<br>"

def getBagItems(item):
    result = []
    i = 0
    for p in item.gff['ItemList']:
        gff_inst = GffInstance(item.gff, 'ItemList', i)
        st_inst = ItemInstance(gff_inst, item)

        equip_slot = p['_STRUCT_TYPE_']
        result.append((equip_slot, st_inst))
        i += 1

    return result

def getPC(bicFile):
    pc = PlayerCharacter(bicFile, DirectoryContainer("./tmp/"))
    return pc

def getGFFItemsFromPC(pc, params):
    exclude_equips = params["exclude_equips"]    
    print(params)
    equips = pc.equips
    if(exclude_equips):
        equips = []
    items = pc.items
    equips.extend(items)
    bags = []
    #fill the lists
    for x in range(len(equips)):
        item = ItemInstance(equips[x][1], pc)
        item = item.gff
        
        # BAG OF HOLDING SCAN ITEMS
        if item.base_type == 66:
            bags.extend(getBagItems(item))

    equips.extend(bags)
    
    ## Build a list of items and their properties
    items = []
    i = 0
    for rg in range(len(equips)):
       i = i + 1
       item = ItemInstance(equips[rg][1], rg)
       item = item.gff
       items.append(item)
    return items

def rawGetItems(bicFile):
    items_str = ""
    #bicFile = "illir1.bic" #sys.argv[1]
    pc = PlayerCharacter(bicFile, DirectoryContainer("./tmp/"))
    #TODO get portrait etc
    #TODO print(pc.get_name_first())

    equips = pc.equips
    items = pc.items 
    equips.extend(items) 
    bags = [] 
    #fill the lists 
    for x in range(len(equips)):
        item = ItemInstance(equips[x][1], pc)
        item = item.gff
        
        # BAG OF HOLDING SCAN ITEMS        
        if item.base_type == 66:
            bags.extend(getBagItems(item))            

    equips.extend(bags)
    
    #iterate over all items including bag contents
    i=0
    for z in range(len(equips)):
        i=i+1
        item = ItemInstance(equips[z][1], z)
        item = item.gff
        items_str += printItem(item, tlk)
        properties = item.properties
        
        for y in range(len(properties)):
            prop = ItemProperty(properties[y], item)
            prop = prop.gff
            items_str += printProperty(prop)   
            
    items_str += "TOTAL : " + str(i) + " ITEMS"
    return items_str
                       

