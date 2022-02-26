import baseLib


def buildBaseItemFilters(params):
    filters = []
    baseItems = baseLib.getBaseItemList()
    for x in range (len(baseItems)):        
        if("filter_"+str(x) in params):
            filters.append(x)
    return filters            

def isFiltered(item, params):
    return item.baseItemCode in params["filterBaseItems"]
