import json
import Config
from core import Localization

exportsPath = Config.gameFilesPath / "DeadByDaylight"

# Maps customization categories to short strings
categoryMap = {
    "ECustomizationCategory::SurvivorHead": "heads",
    "ECustomizationCategory::SurvivorTorso": "torsos",
    "ECustomizationCategory::SurvivorLegs": "legs",
    "ECustomizationCategory::Charm": "charms",
    "ECustomizationCategory::KillerHead": "heads",
    "ECustomizationCategory::KillerBody": "bodies",
    "ECustomizationCategory::KillerWeapon": "weapons",
    "ECustomizationCategory::Badge": "badges",
    "ECustomizationCategory::Banner": "banners"
}

# Item categories which do not have an associated character
universalCategories = ["charms", "badges", "banners"]

# Maps killer item categories to their killer specific subcategories (for example, the Dredge head slot is used as an arm slot)
killerCategoryMap = {
    0: ["masks", "bodies", "weapons"], # Trapper
    2: ["upperBodies", "legs", "weapons"], # Hillbilly
    7: ["masks", "bodies", "weapons"], # Huntress
    10: ["masks", "bodies", "weapons"], # Pig
    13: ["masks", "bodies", "weapons"], # Legion
    14: ["masks", "bodies", "weapons"], # Plague
    15: ["masks", "bodies", "weapons"], # Ghost Face
    17: ["masks", "bodies", "weapons"], # Oni
    27: ["arms", "bodies", "weapons"], # Dredge
    38: ["heads", "legs", "upperBodies"], # Ghoul
}

# Item rarities (values are pulled from the wiki)
rarityMap = {
    "EItemRarity::Common": 1,
    "EItemRarity::Uncommon": 2,
    "EItemRarity::Rare": 3,
    "EItemRarity::VeryRare": 4,
    "EItemRarity::Legendary": 7,
    "EItemRarity::Ascended": 12,
    "EItemRarity::Visceral": 13
}

# These outfits already exist under a different ID and should be ignored
ignoredOutfits = ["Laurie_outfit_006", "MT_outfit_022_CS"]
ignoredItems = ["Default_Badge", "Default_Banner"]

def getDescription(data):
    desc = data["UIData"]["Description"]
    # Use the collection description if no description is present
    if desc.get("LocalizedString") == "\t":
        desc = data["CollectionDescription"]
    elif not (("Namespace" in desc or "TableId" in desc) and "Key" in desc):
        desc = data["CollectionDescription"]
    return desc

def getActualCategory(category, character, killer):
    if killer:
        # Masks, bodies, and weapons correspond to killer slots
        if character in killerCategoryMap:
            if category == "heads":
                return killerCategoryMap[character][0]
            elif category == "bodies":
                return killerCategoryMap[character][1]
            elif category == "weapons":
                return killerCategoryMap[character][2]
    else:
        # Heads, torsos, and legs correspond to survivor slots
        if character == 16 and category == "heads":
            # Ashley is the only survivor with nonstandard cosmetic slots
            return "hands"
    return category

survivorIndexOverrides = {
    # Game order: Kate, Quentin, Tapp
    # Wiki order: Quentin, Tapp, Kate
    10: 12,
    11: 10,
    12: 11
}

killerIndexOverrides = {
    # Game order: Hag, Shape
    # Wiki order: Shape, Hag
    4: 5,
    5: 4
}

def getCharacter(index):
    # 268435456 is the CharacterIndex of K01, so if AssociatedCharacter is greater than or equal to this value, the character is a killer
    if index >= 268435456:
        index -= 268435456
        return killerIndexOverrides.get(index, index), True
    else:
        return survivorIndexOverrides.get(index, index), False

# Loads a single CustomizationItemDB.json file
def loadCustomizationItemDB(path):
    itemDB = []
    with open(path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        rows = data[0]["Rows"]
        for key, entry in rows.items():
            # Category
            category = entry["category"]
            if not category in categoryMap:
                continue
            category = categoryMap[category]
            item = {
                "id": None,
                "key": key,
                "name": entry["UIData"]["DisplayName"],
                "desc": getDescription(entry),
                "rarity": rarityMap[entry["Rarity"]],
                "filename": entry["UIData"]["IconAssetList"][0]["AssetPathName"].split("/")[-1].split(".")[0] + ".png",
                "collectionName": entry["CollectionName"]
            }
            # Default
            if entry.get("IsEntitledByDefault", False):
                item["default"] = True
            # Skip this for charms, badges, and banners since they are universal
            if not category in universalCategories:
                # Character
                character, killer = getCharacter(entry["AssociatedCharacter"])
                # Map the category to a subcategory based on the character
                category = getActualCategory(category, character, killer)
                # Add 1 to the survivor/killer since lua has 1-based indexing
                item["killer" if killer else "survivor"] = character + 1
            item["category"] = category
            itemDB.append(item)
    return itemDB

# Loads a single OutfitDB.json file
def loadOutfitDB(path):
    outfitDB = []
    with open(path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        rows = data[0]["Rows"]
        for key, entry in rows.items():
            outfitDB.append({
                "id": None,
                "key": key,
                "name": entry["UIData"]["DisplayName"],
                "desc": getDescription(entry),
                "filename": entry["UIData"]["IconAssetList"][0]["AssetPathName"].split("/")[-1].split(".")[0] + ".png",
                "pieces": entry["OutfitItems"]
            })
    return outfitDB

def loadFiles(name, loadFunction):
    files = []
    for path in sorted(exportsPath.rglob(name)):
        files.append(loadFunction(path))
    return files

# Loads all CustomizationItemDB.json files
def loadCustomizationItems():
    itemDBList = loadFiles("CustomizationItemDB.json", loadCustomizationItemDB)
    items = {}
    ids = {}
    for itemDB in itemDBList:
        for item in itemDB:
            key = item["key"]
            if key in ignoredItems:
                continue
            category = item["category"]
            if not category in ids:
                ids[category] = 1
            item["id"] = ids[category]
            items[key] = item
            ids[category] += 1
    return items

# Loads all OutfitDB.json files
def loadOutfits():
    outfitDBList = loadFiles("OutfitDB.json", loadOutfitDB)
    outfits = {}
    for outfitDB in outfitDBList:
        for outfit in outfitDB:
            key = outfit["key"]
            if key in ignoredOutfits:
                continue
            outfit["id"] = len(outfits) + 1
            outfits[key] = outfit
    return outfits

# Creates a dict of unique collections {localizedString: {id: collectionId, name: collectionName}} and gives each item its corresponding collectionId
def extractCollections(items):
    collections = {}
    for key, item in items.items():
        collectionId = None
        collectionName = item["collectionName"]
        identifier = Localization.getBestString(collectionName, "en")
        if identifier is not None:
            stripped = identifier.lower().strip()
            if stripped in collections:
                collectionId = collections[stripped]["id"]
            else:
                collectionId = len(collections) + 1
                collections[stripped] = {
                    "id": collectionId,
                    "name": collectionName
                }
        if collectionId is not None:
            item["collectionId"] = collectionId
        del item["collectionName"]
    return collections

def addCrossReferences(items, outfits):
    usedItems = []
    for key, outfit in outfits.items():
        # Make outfits reference their pieces by ID instead of key
        pieceKeys = outfit["pieces"]
        pieces = {}
        for pieceKey in pieceKeys:
            usedItems.append(pieceKey)
            if pieceKey in items:
                piece = items[pieceKey]
                pieces[piece["category"]] = piece["id"]
            else:
                print(f"Outfit {key} includes item {pieceKey} which does not exist!")
        outfit["pieces"] = pieces
        # Copy rarity, collectionId, default, and survivor/killer up to the outfit
        firstPiece = items[pieceKeys[0]]
        outfit["rarity"] = firstPiece["rarity"]
        if "collectionId" in firstPiece:
            outfit["collectionId"] = firstPiece["collectionId"]
        if "default" in firstPiece:
            outfit["default"] = firstPiece["default"]
        role = "killer" if "killer" in firstPiece else "survivor"
        outfit[role] = firstPiece[role]
    return usedItems

def parse():
    items = loadCustomizationItems()
    outfits = loadOutfits()
    collections = extractCollections(items)
    return items, outfits, collections