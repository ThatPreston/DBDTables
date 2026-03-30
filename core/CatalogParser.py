import math
import Config
from utils import FileManager

validItemTypes = ["Head", "Torso", "Legs", "Weapon"]

def reformatReleaseDate(s):
    date = s.split("T")[0]
    components = reversed(date.split("-"))
    separator = "."
    return separator.join(components)

def createItem(entry):
    metaData = entry["metaData"]
    purchasable = entry["purchasable"]
    costs = {}
    if purchasable:
        for cost in entry["defaultCost"]:
            currency = cost["currencyId"]
            price = cost["price"]
            costs[currency] = price
    item = {
        "purchasable": purchasable,
        "rDate": reformatReleaseDate(metaData["releaseDate"])
    }
    if metaData.get("unbreakable", False):
        item["linked"] = True
    if "Cells" in costs:
        item["ac"] = costs["Cells"]
    if "Shards" in costs:
        item["is"] = costs["Shards"]
    return item

def createOutfit(entry):
    metaData = entry["metaData"]
    outfit = {
        "purchasable": entry["purchasable"],
        "rDate": reformatReleaseDate(metaData["releaseDate"]),
        "items": metaData["items"],
        "discountPercentage": metaData["discountPercentage"]
    }
    if metaData.get("unbreakable", False):
        outfit["linked"] = True
    return outfit

def createTables(data):
    items = {}
    outfits = {}
    for entry in data:
        category = entry["categories"][0]
        if category == "item":
            key = entry["id"]
            metaData = entry["metaData"]
            itemType = metaData["type"]
            if itemType in validItemTypes:
                items[key] = createItem(entry)
        elif category == "outfit":
            key = entry["id"]
            outfits[key] = createOutfit(entry)
    return items, outfits

# Usually only individual items have prices, whereas outfits have a "discountPercentage"
# To get the price of an outfit, sum the prices of its items, then apply the discount (for example, 400 + 400 + 400 = 1200, 1200 * 0.9 = 1080)
# The discount percentage only applies to the price in auric cells, iridescent shard prices are unaffected
def calculateOutfitPrices(items, outfits):
    for outfitKey, outfit in outfits.items():
        outfitItems = outfit["items"]
        if outfit["purchasable"]:
            totalPriceCells = 0
            totalPriceShards = 0
            for itemKey in outfitItems:
                item = items.get(itemKey)
                if item is not None:
                    cells = item.get("ac")
                    if cells is not None:
                        totalPriceCells += cells
                    shards = item.get("is")
                    if shards is not None:
                        totalPriceShards += shards
                else:
                    print(f"Outfit \"{outfitKey}\" includes item \"{itemKey}\" which does not exist!")
            if totalPriceCells > 0:
                discountedPrice = math.floor(totalPriceCells * (1 - outfit["discountPercentage"]))
                outfit["ac"] = discountedPrice
            if totalPriceShards > 0:
                outfit["is"] = totalPriceShards
        del outfit["items"]
        del outfit["discountPercentage"]

def parse():
    data = FileManager.loadBackendFile("catalog.json", Config.gameVersion)
    if data is not None:
        items, outfits = createTables(data)
        calculateOutfitPrices(items, outfits)
        return {"items": items, "outfits": outfits}
    return None

specialCatalogKeys = {
    "US_Outfit_023": "US_outfit_023"
}

# Reads the catalog file and appends data to the cosmetic tables
def appendData(items, outfits):
    catalog = parse()
    if catalog is None:
        print("Catalog not found!")
        return False

    for itemKey, data in catalog["items"].items():
        item = items.get(itemKey)
        if item is not None:
            item.update(data)
            if not "rDate" in item:
                print(f"Item \"{itemKey}\" has no release date!")

    for outfitKey, data in catalog["outfits"].items():
        # For any case where the outfit ID in the catalog is different from the actual outfit ID
        if outfitKey in specialCatalogKeys:
            outfitKey = specialCatalogKeys[outfitKey]
        outfit = outfits.get(outfitKey)
        if outfit is not None:
            outfit.update(data)
            if not "rDate" in outfit:
                print(f"Outfit \"{outfitKey}\" has no release date!")

    return True