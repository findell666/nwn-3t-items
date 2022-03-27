import sys
import os
import io
import baseLib

from pynwn.player_character import PlayerCharacter
from pynwn.item import ItemProperty
from pynwn.file.tlk import Tlk

dialog = os.path.join("./resources/tlk/", 'dialog.tlk')    
tlk = Tlk(open(dialog, 'rb'))


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

class ItemWrapper:
    name=""
    baseItem=""
    baseItemCode=""
    displayName=""
    tag=""
    descId=""
    comment=""
    owner=""
    cost=""
    level=""
    tier=""
    resref=""
    properties = []
    propertiesDictionnary = {}        
    tagsSeen = {}
    gffItem=None

    def __init__(self, gffItem, owner, params):
        self.properties = []
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

        # perfs ??
        self.unicityString = self.owner+self.resref+self.name+self.displayName
        if(self.unicityString in ItemWrapper.tagsSeen):
            ItemWrapper.tagsSeen[self.unicityString] = ItemWrapper.tagsSeen[self.unicityString] + 1
        else:
            ItemWrapper.tagsSeen[self.unicityString] = 1

        # set the properties
        properties = gffItem.properties

        for y in range(len(properties)):
            prop = ItemProperty(properties[y], gffItem)
            prop = prop.gff

            propn = prop.gff["PropertyName"]
            sub = prop.gff["Subtype"]
            cost = prop.gff["CostValue"]

            propNameString = str(baseLib.getPropertyName2DAValue(propn))
            propSubTypetring = str(baseLib.getSubType2DAResRef(propn, sub)) 
            propValue = str(baseLib.getCostValue2DAResRef(propn, sub, cost))

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

            # if expanded it's whole property
            if(expanded):
                self.addProperty(propn, prop.type, sub, cost, propNameString, propSubTypetring, propValue, prop, expanded)
            # if not expanded we add the value to existing one
            else:
                found = False
                for z in range(len(self.properties)):
                    currentProp = self.properties[z]
                    if(currentProp.id == propn and currentProp.propType == prop.type):
                        currentProp.value = currentProp.value + " " +  propSubTypetring + " "+ propValue
                        found = True
                        break
                if(not found):
                    self.addProperty(propn, prop.type, sub, cost, propNameString, propSubTypetring, propValue, prop, expanded)                         

                                
            # indexStr = str(propNameString)

            # # define new array for stats[index]
            # if indexStr not in stats.keys():        
            #     stats[indexStr] = []

            # stats[indexStr].append({propString: propValue})        

        # calculate price and level req
        # self.price = self.calculatePrice()

        #at the end
        self.buildPropertyDictionnary()
        pass

    def calculatePrice(self):

        baseCost = baseLib.baseItemCost(self.baseItemCode)
        if(isinstance(baseCost, str)):
            return 0
        Multiplier = 1
        NegMultiplier = 0
        SpellCosts = 0
        MaxStack = 1
        BaseMult = 1
        AdditionalCost = 1

        ItemCost = [baseCost + 1000*(Multiplier*Multiplier - NegMultiplier*NegMultiplier) + SpellCosts]*MaxStack*BaseMult + AdditionalCost        

        return ItemCost

    def getLevelReq(self):
        pass
        # code from 3t, dichotmic search in itemvalue.2da
        # int ItemLevelRequired(object oItem){
        # string s2daName = "itemvalue";
        # int start = 0;
        # int end = 59;
        # int found = 0;
        # int x = -1;
        # int iPrice = GetGoldPieceValue(oItem);
        # int iGoldMin = StringToInt(Get2DAString(s2daName, "MAXSINGLEITEMVALUE", start));
        # if(iPrice < iGoldMin) return 1;
        # int iGoldMax = StringToInt(Get2DAString(s2daName, "MAXSINGLEITEMVALUE", end));
        # if(iPrice >= iGoldMax) return 60;
        # while(found == 0 && start < end){
        # x = start + ((end - start) / 2);
        # int iGoldMin = StringToInt(Get2DAString(s2daName, "MAXSINGLEITEMVALUE", x));
        # int iGoldMax = StringToInt(Get2DAString(s2daName, "MAXSINGLEITEMVALUE", x+1));
        # if (iGoldMax > iPrice && iPrice >= iGoldMin){
        # found = 1;
        # x = x+1;
        # }
        # else if (iGoldMax > iPrice){
        # end = x;
        # }
        # else if (iGoldMin < iPrice){
        # start = x + 1;
        # }
        # }
        # return StringToInt(Get2DAString(s2daName, "LABEL", x));
        # }

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


    def getAllKeys(self):        
        keys = list(self.__dict__.keys())
        keys.remove("properties")
        keys.remove("propertiesDictionnary")
        keys.remove("gffItem")
        keys.remove("unicityString")
        keys.remove("baseItemCode")

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
