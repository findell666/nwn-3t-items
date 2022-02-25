import sys
import os
import io

import baseLib
from Wrapper import ItemWrapper

# Format the items as CSV
def exportAsCSV(items, filePath, params):

    group_duplicates = params["group_duplicates"]
    expand_skills = params["expand_skills"]
    expand_uses = params["expand_uses"]
    expand_abilities = params["expand_abilities"]
    expand_saves = params["expand_saves"]    
    filter_owner = params["filter_owner"]

    # the csv separator
    joinStr  = "; "

    f = open(filePath, 'w')

    #the header is a merge of all keys
    allKeys = []
    for i in range(len(items)):
        item = items[i]
        allKeys.extend(item.getAllKeys())

    allKeysUnsorted = set(allKeys)
    
    # metaDataList
    metaDataList = ["name", "displayName", "nb", "owner", "baseItem", "tier"]
    metaDataListRemove = ["Light", "descId", "resref", "comment", "tag", "****"]
    if(filter_owner):
        metaDataList.remove("owner")
    metaDataHeaderStr = joinStr.join(metaDataList)

    # properties List
    propertiesListSorted = ["Armor Bonus:", "Enhancement Bonus:", "Attack Bonus:", "Ability Bonus:"]
    if(expand_abilities):
        propertiesListSorted.remove("Ability Bonus:")
        propertiesListSorted.extend(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])

    propertiesListSorted.append("Skill Bonus:")
    if(expand_skills):
        propertiesListSorted.remove("Skill Bonus:")
        propertiesListSorted.extend(["Animal Empathy", "Concentration", "Disable Trap", "Discipline", "Heal", "Hide", "Listen", "Lore", "Move Silently", "Open Lock", "Parry", "Perform", "Persuade", "Pick Pocket", "Search", "Set Trap", "Spellcraft", "Spot", "Taunt", "Use Magic Device", "Appraise", "Tumble", "Craft Trap", "Bluff", "Intimidate", "Craft Armor", "Craft Weapon"])

    propertiesListSorted.append("Saving Throw:")
    if(expand_saves):
        propertiesListSorted.remove("Saving Throw:")
        # TODO list of saving throws here
        propertiesListSorted.extend([])

    propertiesListSorted.append("Damage Resistance:")
         

    allKeysUnsorted = allKeysUnsorted - set(metaDataListRemove)
    allKeysUnsorted = allKeysUnsorted - set(propertiesListSorted)
    restOfPropsUnsorted = allKeysUnsorted - set(metaDataList)
    restOfPropsUnsorted = list(restOfPropsUnsorted)

    propertiesListSorted.extend(restOfPropsUnsorted)
    
    finalPropertiesList = propertiesListSorted
    finalPropertiesListStr = joinStr.join(finalPropertiesList)

    # HEADER (metaData + properties)
    f.write(metaDataHeaderStr+";"+finalPropertiesListStr)

    #ROWS
    for i in range(len(items)):
        item = items[i]
        currentStats = [] #the list of properties to be displayed per row
        nbSeen = ItemWrapper.tagsSeen[item.unicityString]
        if(nbSeen == 0): 
            continue
        # well already saw the item
        if(group_duplicates):
            ItemWrapper.tagsSeen[item.unicityString] = 0

        #metadata first
        for m in range(len(metaDataList)):
            key = metaDataList[m]
            if(key == "nb"):
                currentStats.append(str(nbSeen))             
            else:
                prop = item.renderItem().get(key, "")
                currentStats.append(prop)

        #then properties
        for p in range(len(finalPropertiesList)):
            key = finalPropertiesList[p]
            prop = item.getPropertyByName(key)        
            if(None == prop):
                 currentStats.append("")
                 continue
            currentStats.append("\""+prop.getValue()+"\"")
            #currentStats.append(itemsBuilder.statToCSVString(stat))
        f.write("\n")
        f.write(joinStr.join(currentStats))
        
    f.close
    
    
def runExportAsCSV(bicFiles, dir, origFileNames, params):

    items = []
    for iii in range(len(bicFiles)):
        exclude_equips = params["exclude_equips"]

        pc = baseLib.getPC(bicFiles[iii])

        gffItems = baseLib.getGFFItemsFromPC(pc, params)

        ## Build a list of items and their properties        
        i = 0
        for rg in range(len(gffItems)):
            i = i + 1

            itemWrapper = ItemWrapper(gffItems[rg], origFileNames[iii], params)            

            #filter objects
            filter_scrolls = params["filter_scrolls"]
            filter_keys = params["filter_keys"]
            filter_potions = params["filter_potions"]    
            filter_trinkets = params["filter_trinkets"]
            filter_blank_scroll = params["filter_blank_scroll"]
            filter_gems = params["filter_gems"]
            filter_bag = params["filter_bag"]

            #filters
            baseItem = itemWrapper.baseItemCode
            if((filter_scrolls and 75 == baseItem) or (filter_keys and 65 == baseItem) or
            (filter_potions and 49 == baseItem) or (filter_trinkets and 24 == baseItem) or
            (filter_blank_scroll and 102 == baseItem) or (filter_gems and 77 == baseItem) or
            (filter_bag and 66 == baseItem)):
                continue

            items.append(itemWrapper)

    csvFileName = origFileNames[0]+".csv"        
    if(len(bicFiles) > 1):
        csvFileName = "multiple chars"+".csv"

    exportAsCSV(items, os.path.join(dir, csvFileName), params)
    return csvFileName