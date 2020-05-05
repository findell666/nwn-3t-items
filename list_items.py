#!/usr/bin/env python

import sys
import os
import io

from pynwn.player_character import PlayerCharacter
from pynwn.item import ItemInstance
from pynwn.item import Item
from pynwn.item import ItemProperty
from pynwn.resource import DirectoryContainer
from pynwn.file.gff import GffInstance
from pynwn.file.tlk import Tlk

#tiers
#whishlist

dialog = os.path.join("./resources/tlk/", 'dialog.tlk')    
tlk = Tlk(open(dialog, 'rb'))

ITEMPROPDEF = "./resources/2da/itempropdef.2da"

#chelou ces 3
#1 - 9, 22, 45, 56 - 59 Enhancement, Attack, AC, ... : ("./resources/2da/iprp_bonuscost.2da", 1, 2)
#4, 8, 18, 58, 64 Racial_Type : ("./resources/2da/racialtypes.2da", 3, 1)
#5, 9, 19, 59, 65 Specific_Alignment : ("./resources/2da/iprp_alignment.2da", 1, 2)

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

Specific_Alignment = ("./resources/2da/iprp_alignment.2da", 1, 2)
Racial_Type = ("./resources/2da/racialtypes.2da", 3, 1)

AC_Type = ("./resources/2da/iprp_acmodtype.2da", 1, 2)
Ability = ("./resources/2da/iprp_abilities.2da", 1, 2)
Alignment_Group = ("./resources/2da/iprp_aligngrp.2da", 1, 2)
Bonus_Feat = ("./resources/2da/iprp_feats.2da", 1, 2)
Cast_Spell = ("./resources/2da/iprp_spells.2da", 2, 1)
Class = ("./resources/2da/classes.2da", 2, 1)
Damage_Type = ("./resources/2da/iprp_damagetype.2da", 1, 2)
Extra_Melee_Damage_Type = ("./resources/2da/iprp_combatdam.2da", 1, 2)
Immunity = ("./resources/2da/iprp_immunity.2da", 1, 2)
IMMU_COST = ("./resources/2da/iprp_immuncost.2da", 1, 2)
Immunity_Spell_School = ("./resources/2da/spellschools.2da", 3, 1)

ON_HIT_COST = ("./resources/2da/iprp_onhitcost.2da", 1, 2)
ON_HIT_DUR = ("./resources/2da/iprp_onhitdur.2da", 1, 2)

On_Hit = ("./resources/2da/iprp_onhit.2da", 1, 2)
On_Hit_Cast_Spell = ("./resources/2da/iprp_onhitspell.2da", 2, 1)
On_Monster_Hit = ("./resources/2da/iprp_monsterhit.2da", 1, 2)
Poison_On_Monster_Hit = ("./resources/2da/poison.2da", 2, 1)
Saving_Throw_Bonus = ("./resources/2da/iprp_saveelement.2da", 1, 2)
Saving_Throw_Bonus_Specific = ("./resources/2da/iprp_savingthrow.2da", 1, 2)
Skill = ("./resources/2da/skills.2da", 2, 1)
Special_Walk = ("./resources/2da/iprp_walk.2da", 1, 2)
Trap = ("./resources/2da/iprp_traps.2da", 1, 2)
Unlimited_Ammunition = ("./resources/2da/iprp_ammotype.2da", 1, 2)
Visual_Effect = ("./resources/2da/iprp_visualfx.2da", 2, 1)


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
        28: Class, #AC_Type,
        0 : Ability, #, KEEN TOut ça
        27: Class, #Ability, 
        2 : Ability,
        7 : Alignment_Group,
        17: Alignment_Group,
        57: Alignment_Group,
        62: Alignment_Group,
        12 : Bonus_Feat,
        15 : Cast_Spell,
        13 : Class,
        63 : Class,
        10 : Damage_Type,        
        16 : Damage_Type,
        20 : Damage_Type,
        23 : Damage_Type,
        24 : Damage_Type,
        3 : Extra_Melee_Damage_Type,
        33 : Extra_Melee_Damage_Type, 
        34 : Extra_Melee_Damage_Type,
        37 : Immunity,
        54 : Immunity_Spell_School,
        48 : On_Hit,
        82 : On_Hit_Cast_Spell,
        72 : On_Monster_Hit,
        21 : Poison_On_Monster_Hit,
        4 : Racial_Type,
        8 : Racial_Type,
        18 : Racial_Type,
        58 : Racial_Type,
        64 : Racial_Type, 
        40 : Saving_Throw_Bonus,
        49 : Saving_Throw_Bonus,
        41 : Saving_Throw_Bonus_Specific,
        50 : Saving_Throw_Bonus_Specific,
        29 : Skill, 
        52 : Skill,
        79 : Special_Walk,
        5 : Specific_Alignment,
        9 : Specific_Alignment,
        19 : Specific_Alignment,
        59 : Specific_Alignment,
        65 : Specific_Alignment ,
        70 : Trap,
        61 : Unlimited_Ammunition,
        83 : Visual_Effect,
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
    if prop in (0, 1, 6, 51, 40, 41, 67):
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
        return (Racial_Type, True)        
    

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
    print("----------------ITEM FOUND--------------------")
    #essayer de récuper le resref ici quand None pour aller cher la string dans le tlk
    if None != item.get_name(0) and "None" != item.get_name(0):
        print("NAME : " + str(item.get_name(0)))
    else:
        if None == tlk:
            print("NAME : " + str(item.get_name()))
        else:
            print("NAME : " + str(tlk.__getitem__(item.get_name())))
    #print("DESC : " + str(item.get_description(0)))
    print("DESC ID : " + str(item.get_description_id(0)))
    print("DISPLAY NAME : " + str(item.display_name))
    print("BASEITEM : " + str(item.base_type))    
    #print("COMMENT : " + str(item.comment))       
    print("TAG : " + str(item.tag))   

def printProperty(prop):
    print("Property : ")
    propn = prop.gff["PropertyName"]
    sub = prop.gff["Subtype"]
    cost = prop.gff["CostValue"]
    print("        PropertyName : " + str(propn))
    print("        Subtype : " + str(sub))
    print("        CostValue : " + str(cost))
    print("        Param1 : " + str(prop.gff["Param1"]))
    print("        Param1Value : " + str(prop.gff["Param1Value"]))
    print("        UsesPerDay : " + str(prop.gff["UsesPerDay"]))
    #print("        Useable : " + str(prop.gff["Useable"]))
    #print("        CustomTag : " + str(prop.gff["CustomTag"]))
    print("        Prop string : " + str(getPropertyName2DAValue(propn)) + " " + str(getSubType2DAResRef(propn, sub)) + " " + str(getCostValue2DAResRef(propn, sub, cost)))
    #print("        Param1 : " + str(getParam12DAResRef(propn, sub, prop.gff["Param1"])))  
    print("        Param1Value : " + str(getParam1Value2DAResRef(propn, sub, prop.gff["Param1"], prop.gff["Param1Value"])))      


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

if __name__ == '__main__':

    bicFile = sys.argv[1]
    pc = PlayerCharacter(bicFile, DirectoryContainer("./"))
    #TODO get portrait etc
    print("----")
    #TODO print(pc.get_name_first())
    print("----")    

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
        printItem(item, tlk)
        properties = item.properties
        
        for y in range(len(properties)):
            prop = ItemProperty(properties[y], item)
            prop = prop.gff
            printProperty(prop)   
            
    print("TOTAL : " + str(i) + " ITEMS");                 

