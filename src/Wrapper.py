import sys
import os
import io
import baseLib

from pynwn.player_character import PlayerCharacter
from pynwn.item import ItemProperty
from pynwn.file.tlk import Tlk

dialog = os.path.join("./resources/tlk/", 'dialog.tlk')    
tlk = Tlk(open(dialog, 'rb'))

condensedDict = {"Strength" : "STR", "Dexterity" : "DEX", "Constitution" : "CON", "Intelligence": "INT", "Wisdom" : "WIS", "Charisma" : "CHA",
"Reflex" : "reflex", "Fortitude" : "fort", "Universal" : "univ", "Mind Affecting" : "mind", "Spellcraft"  : "sc", "Animal Empathy" : "ae", "Move Silently": "ms", "Spot" : "spot", "Craft Weapon" : "cw", "Use Magic Device" : "umd",
"Discipline" : "disc", "Concentration": "conc",
"Spell Resistance:" : "SR",
"Regeneration:" : "regen", "Immunity:" : "Immunity", 
"Armor Bonus:" : "AC", "Enhancement Bonus:" : "EB",
"Electrical Resist" : "elect res", "Acid Resist" : "acid res",
"Positive Energy" : "pos",
"Spell Penetration" : "Spell pen", "Wizard" : "wiz",
}

def statToCSVString(stat):
    statStr = ""
    if isinstance(stat, list):
        statsStrs = []
        for k in range(len(stat)):
            if isinstance(stat[k], dict):         
                #normally only one pair by element       
                for key, value in stat[k].items():
                    statsStrs.append(key + " " + value)

            else:
                #we never go here
                statsStrs.append(stat[k])
        
        statStr = ", ".join(statsStrs)
    else:
        statStr = stat

    return statStr

def toCondensedString(string):
    if(string in condensedDict):
        return condensedDict[string]
    else:
        return string

def getInventoryItemPositionString(x, y):
    nthTab = int(y / 6) + 1
    row = (y % 6)
    col = x + 1
    return "tab " + str(nthTab) + " row " + str(row) + " col " + str(col)

class ItemWrapper: 

    equip_slots = {
        1 : "helmet slot",
        2: "armor slot",
        4 : "boots slot", 
        8 : "bracers slot",
        16 : "right hand slot",
        32 : "left hand slot",
        64 : "cloak slot",
        128 : "ring slot",
        256 : "ring slot",
        512 : "amulet slot",
        1024 : "belt slot",
        2048 : "arrow slot",
        4096 : "bullet slot",
        8192 : "bolt slot",
    }
    tagsSeen = {}

    def __init__(self, gffItem, owner, params):
        self.properties = []
        self.propertiesRaw = [] #to create condensed column
        self.propertiesDictionnary = {}

        self.gffItem = gffItem
        self.owner = owner
        expand_skills = params["expand_skills"]
        expand_uses = params["expand_uses"]
        expand_abilities = params["expand_abilities"]  
        expand_dr = params["expand_dr"]
        expand_saves = params["expand_saves"]

        # metadata
        if None != gffItem.get_name(0) and "None" != gffItem.get_name(0):
            self.name = str(gffItem.get_name(0))
        else:
            if None == tlk:
                self.name = str(gffItem.get_name())
            else:
                self.name = str(tlk.__getitem__(gffItem.get_name()))

        displayName = str(gffItem.display_name)
        if(None == displayName or 'None' == displayName):
            displayName = ""
        descId = str(gffItem.get_description_id(0))
        if(None == descId or 'None' == descId):
            descId = ""
        comment = str(gffItem.comment)
        if(None == comment or 'None' == comment):
            comment = ""

        baseItem = gffItem.base_type
        self.baseItem = baseLib.getBaseItemName(baseItem)
        self.baseItemCode = baseItem
        self.tag = str(gffItem.tag)
        self.displayName = displayName.replace("\n", " - ").replace(";", " - ")
        self.descId = descId.replace("\n", " - ").replace(";", " - ")
        self.comment = comment.replace("\n", " - ").replace(";", " - ")
        self.tier = self.getTier()
        self.resref = gffItem.resref
        self.additionalCost = gffItem.cost_additional
        self.castSpellCosts = []

        # render position
        if gffItem.parentContainer == "equipment" and 131072 != gffItem.pos:
            self.position = self.equip_slots[gffItem.pos]

        if gffItem.parentContainer == "inventory":
            x = gffItem.pos[0].val
            y = gffItem.pos[1].val + 1            
            self.position = getInventoryItemPositionString(x, y)

        if gffItem.parentContainer == "bag":
            x = gffItem.pos[0].val
            y = gffItem.pos[1].val + 1
            xBag = gffItem.parentPos[0].val
            yBag = gffItem.parentPos[1].val + 1
            row = y
            col = x + 1
            self.position = "bag " + getInventoryItemPositionString(xBag, yBag) + ", row " + str(row) + " col " + str(col)            

        # print(self.name + " "  +self.displayName)

        # perfs ??
        self.unicityString = self.owner+self.resref+self.name+self.displayName
        if(self.unicityString in ItemWrapper.tagsSeen):
            ItemWrapper.tagsSeen[self.unicityString] = ItemWrapper.tagsSeen[self.unicityString] + 1
        else:
            ItemWrapper.tagsSeen[self.unicityString] = 1

        print(self.name +  "" + self.displayName)

        # set the properties
        properties = gffItem.properties
        self.negMultiplier = 0
        self.multiplier = 0
        for y in range(len(properties)):
            prop = ItemProperty(properties[y], gffItem)
            prop = prop.gff

            propn = prop.gff["PropertyName"]
            sub = prop.gff["Subtype"]
            cost = prop.gff["CostValue"]

            #quickfix for the +x part of soak items
            if(propn == 22):
                sub = sub + 1

            propNameString = str(baseLib.getPropertyName2DAValue(propn))
            propSubTypetring = str(baseLib.getSubType2DAResRef(propn, sub)) 
            propValue = str(baseLib.getCostValue2DAResRef(propn, sub, cost))

            if propValue == "65535":
                propValue = ""

            expanded = False
            # fix EB and Abilities mixed up together under same propn
            if(prop.type == 0):
                propNameString = "Ability Bonus:"

            if(expand_skills and 52 == propn):
                propNameString = propSubTypetring
                propString = ""
                expanded = True
                
            if((expand_uses and 15 == propn) or (expand_dr and 23 == propn)):
                propNameString = propNameString + " " + propSubTypetring
                propString = ""
                expanded = True

            if((expand_abilities and 0 == propn) or (expand_saves and (40 == propn or 49 == propn))):
                 propNameString = propSubTypetring
                 propString = "" 
                 expanded = True

            # Save throws "Save" + name in the header, just the value in the column
            if((expand_saves and (40 == propn or 49 == propn))):
                propNameString = "Save " + propSubTypetring
                propString = ""
                expanded = True

            # calculate the property cost 
            #To calculate the cost of a single Item Property, use the following formula:
            #ItemPropertyCost = PropertyCost + SubtypeCost + CostValue
            
            # If an Item Property has a PropertyName of 15 (Cast Spell), then omit it from the Multiplier/NegMultiplier totals. 
            # It will be handled when calculating the SpellCosts instead.
            PropertyCost = 0 #ItemPropertyWrapper.getPropertyCost(prop)
            SubtypeCost = 0 #ItemPropertyWrapper.getSubtypeCost(prop, PropertyCost)
            CostValue = 0 #ItemPropertyWrapper.getCostValue(prop)
            #print("PropertyCost " + str(PropertyCost))
            #print("SubtypeCost " + str(SubtypeCost))
            #print("CostValue " + str(CostValue))
            if(propn != 15):                
                ItemPropertyCost = PropertyCost + SubtypeCost + CostValue
                if(ItemPropertyCost < 0):
                    self.negMultiplier += ItemPropertyCost
                else:
                    self.multiplier += ItemPropertyCost

            if(propn == 15):
                self.castSpellCosts.append((PropertyCost + CostValue)* SubtypeCost)

            self.addPropertyRaw(propn, prop.type, sub, cost, propNameString, propSubTypetring, propValue, prop, expanded)
            
            # if expanded it's whole property (this code shouldnt be here, move it to csvExport.py)
            if(expanded):
                self.addProperty(propn, prop.type, sub, cost, propNameString, propSubTypetring, propValue, prop, expanded)
            # if not expanded we add the value to existing one
            else:
                found = False
                for z in range(len(self.properties)):
                    currentProp = self.properties[z]
                    if(currentProp.id == propn and currentProp.propType == prop.type):
                        currentProp.value = currentProp.value + " " +  propSubTypetring + " " + propValue
                        found = True
                        break
                if(not found):
                    self.addProperty(propn, prop.type, sub, cost, propNameString, propSubTypetring, propValue, prop, expanded)                         

                                
            # indexStr = str(propNameString)

            # # define new array for stats[index]
            # if indexStr not in stats.keys():        
            #     stats[indexStr] = []

            # stats[indexStr].append({propString: propValue})

        #at the end

        #compile properties into a single string
        self.condensedString = self.name + " : "
        for z in range(len(self.propertiesRaw)):
            currentProp = self.propertiesRaw[z]

            if(not currentProp.value):
                self.condensedString += toCondensedString(currentProp.name) + " " + toCondensedString(currentProp.subType) + ", "
            else:
                nameStr = toCondensedString(currentProp.name)
                if(currentProp.subType):
                    nameStr = toCondensedString(currentProp.subType)
                self.condensedString += nameStr + " " + toCondensedString(currentProp.value) + ", "

        self.condensedString = self.condensedString[:-2]
        # calculate price and level req
        self.price = self.calculatePrice()
        self.levelReq = self.getLevelReq()
        self.buildPropertyDictionnary()

    def calculatePrice(self):        
        baseCost = baseLib.baseItemCost(self.baseItemCode)
        if(-1 == baseCost):
            return 0
        baseMult = baseLib.baseMult(self.baseItemCode)
        if(-1 == baseMult):
            return 0

        # AdditionalCost = AddCost Field from the Item Struct.
        additionalCost = self.additionalCost

        #TODO
        Multiplier = self.multiplier
        NegMultiplier = self.negMultiplier        
        MaxStack = 1
        SpellCosts = 0

        # SpellCosts
        # After adjusting the CastSpellCosts, add them up to obtain the total SpellCosts value. 
        # Use the total SpellCosts to calculate the total ItemCost using the formula given at the very beginning of Section 4.4.</code>
        if len(self.castSpellCosts):
            firstMax = max(self.castSpellCosts)
            self.castSpellCosts.remove(firstMax)
            secondMax = 0
            if len(self.castSpellCosts):                     
                secondMax = max(self.castSpellCosts)

            SpellCosts = firstMax + secondMax * 0.75

            for m in range(len(self.castSpellCosts)):
                SpellCosts += self.castSpellCosts[m] * 0.5

        ItemCost = (baseCost + 1000*(Multiplier*Multiplier - NegMultiplier*NegMultiplier) + SpellCosts)*MaxStack*baseMult + additionalCost    
        return int(ItemCost)

    def getLevelReq(self):    
        # code from 3t, dichotmic search in itemvalue.2da
        start = 0
        end = 59
        found = 0
        x = -1
        iPrice = self.price
        iGoldMin = baseLib.getItemvalueVal(start)
        if(iPrice < iGoldMin):
            return 1        
        iGoldMax = baseLib.getItemvalueVal(end)
        if(iPrice >= iGoldMax):
            return 60

        while(found == 0 and start < end):
            x = start + ((end - start) / 2)
            iGoldMin = baseLib.getItemvalueVal(int(x))
            iGoldMax = baseLib.getItemvalueVal(int(x+1))
            if(iGoldMax > iPrice and iPrice >= iGoldMin):
                found = 1
                x = x+1        
            elif(iGoldMax > iPrice):
                end = x   
            elif(iGoldMin < iPrice):
                start = x + 1
        return baseLib.getItemvalueLabel(int(x))

    def getTier(self):
        if(self.tag[0:2] == "bo" or self.tag[0:2] == "it"):
            splitted = self.tag.split("_")
            if(len(splitted) > 2):
                if(self.tag[0:2] == "bo"):
                    if(splitted[1][0:1] == "0"):
                        return "B" + splitted[1][1:2]
                    else:                    
                        return "B" + splitted[1]
                if(self.tag[0:2] == "it"):
                    if(splitted[1][0:1] == "0"):
                        return "T" + splitted[1][1:2]
                    else:
                        return "T" + splitted[1]
        return "" 

    def addProperty(self, id, propType, subId, cost, name, subType, value, gffProp, expanded):
        itemPropertyWrapper = ItemPropertyWrapper(id, propType, subId, cost, name, subType, value, gffProp, expanded)
        self.properties.append(itemPropertyWrapper)

    def addPropertyRaw(self, id, propType, subId, cost, name, subType, value, gffProp, expanded):
        itemPropertyWrapper = ItemPropertyWrapper(id, propType, subId, cost, name, subType, value, gffProp, expanded)
        self.propertiesRaw.append(itemPropertyWrapper)

    def getAllKeys(self):        
        keys = list(self.__dict__.keys())
        keys.remove("properties")
        keys.remove("propertiesRaw")
        keys.remove("propertiesDictionnary")
        keys.remove("gffItem")
        keys.remove("unicityString")
        keys.remove("baseItemCode")
        keys.remove("additionalCost")
        keys.remove("negMultiplier")
        keys.remove("castSpellCosts")
        
        for p in range(len(self.properties)):
            prop = self.properties[p]
            keys.append(prop.name)            
        return keys            

    #make a map property : list index
    def buildPropertyDictionnary(self):
        for p in range(len(self.properties)):
            prop = self.properties[p]
            self.propertiesDictionnary[prop.name] = p

    def getPropertyByName(self, name):
        index = self.propertiesDictionnary.get(name)
        if(index == None):
            return None
        return self.properties[index]

    def renderItem(self):
        return self.__dict__
        

class ItemPropertyWrapper:
    id=""
    propType=""
    subId=""
    cost="" 
    name=""
    subType=""
    value=""    
    isExpanded=False  

    def __init__(self, id, propType, subId, cost, name, subType, value, gffProp, expanded=False):

        self.id = id
        self.propType = propType
        self.subId = subId
        self.cost = cost
        self.name = name
        self.subType = subType
        self.value = str(value)
        self.isExpanded = expanded
        self.gffProp = gffProp
        self.costTable = gffProp.cost_table
        self.costValue = gffProp.cost_value

    def toString(self):
        print("("+str(self.id)+","+str(self.subId)+","+str(self.cost)+","+str(self.name)+","+str(self.subType)+","+str(self.value)+")")

    def getValue(self):
        value = ""
        propString = ""
        if("" == self.subType):
            propString = self.name
        else:
            propString = self.subType

        if(self.isExpanded):
            value = str(self.value)
        else:
            value = propString + " " + str(self.value)
        return value            

    #In itempropdef.2da, get the floating point value in the Cost column, at the row indexed by the PropertyName Field of the ItemProperty Struct. 
    # If the Cost column value is ****, treat it as 0. This floating point value is the PropertyCost.
    def getPropertyCost(gffProp):
        propn = gffProp.gff["PropertyName"]
        cost = baseLib.getPropertyCost2DAValue(propn)
        if(cost == "****"):
            return 0
        return float(cost)
        
        # sub = prop.gff["Subtype"]
        # cost = prop.gff["CostValue"] 
    #If the PropertyCost obtained above from itempropdef.2da was 0, then get the ResRef in the SubTypeResRef column of itempropdef.2da, 
    # at the row indexed by the PropertyName Field of the ItemProperty Struct. This is the resref of the subtype table 2da.
    #In the subtype 2da, get the floating point value in the Cost column at the row indexed by the Subtype Field of the ItemProperty Struct. This floating point value is the SubtypeCost.
    #Only get the SubtypeCost if the PropertyCost was 0. If the PropertyCost was greater than 0, then the SubtypeCost is automatically 0 instead.
    def getSubtypeCost(gffProp, cost):
        propn = gffProp.gff["PropertyName"]
        sub = gffProp.gff["Subtype"]
        cost = gffProp.gff["CostValue"]
        if(cost == 0):
            #print("propn " + str(propn) + " sub " + str(sub) + " cost " + str(cost))
            resRef = baseLib.getSubTypeResRef2DAValue(propn)
            #print("->resRef" + resRef)
            if("IPRP_ALIGNGRP" == resRef or "IPRP_VISUALFX" == resRef):
                return 0
            if("****" == resRef or 255 == resRef):
                resRef = "iprp_bonuscost"
            val = baseLib.getSubtypeCost(resRef, sub)
            return val
        return 0

    #In iprp_costtable.2da, get the string in the Name column at the row indexed by the CostTable Field in the ItemProperty Struct. This is the ResRef of the cost table 2da.
    #In the cost table, get the floating point value in the Cost column in the row indexed by the CostValue Field in the ItemProperty Struct. This floating point value is the CostValue.
    def getCostValue(gffProp):
        costTable = gffProp.cost_table
        costValue = gffProp.cost_value
        resRef = baseLib.getResRefCostTable(costTable)
        if(255 == resRef):
            return 0
        if("****" == resRef or "iprp_base1" == resRef.lower()):
            return 0
        cost = baseLib.getCostValue(resRef, costTable)
        return cost