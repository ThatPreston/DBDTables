import json
import Config

exportsPath = Config.gameFilesPath / "DeadByDaylight"

# Maps customization categories to short strings
# Badges and banners can be uncommented, but I am leaving them out since the original datatables didn't include them
categoryMap = {
    "ECustomizationCategory::SurvivorHead": "heads",
    "ECustomizationCategory::SurvivorTorso": "torsos",
    "ECustomizationCategory::SurvivorLegs": "legs",
    "ECustomizationCategory::Charm": "charms",
    "ECustomizationCategory::KillerHead": "masks",
    "ECustomizationCategory::KillerBody": "bodies",
    "ECustomizationCategory::KillerWeapon": "weapons",
    #"ECustomizationCategory::Badge": "badges",
    #"ECustomizationCategory::Banner": "banners"
}

# Item categories which do not have an associated character
universalCategories = ["charms", "badges", "banners"]

# Maps killer item categories to their killer specific subcategories (for example, the Dredge head slot is used as an arm slot)
killerCategoryMap = [
    ["masks", "bodies", "weapons"], # Trapper
    ["heads", "bodies", "weapons"], # Wraith
    ["upperBodies", "legs", "weapons"], # Hillbilly
    ["heads", "bodies", "weapons"], # Nurse
    ["heads", "bodies", "weapons"], # Shape
    ["heads", "bodies", "weapons"], # Hag
    ["heads", "bodies", "weapons"], # Doctor
    ["masks", "bodies", "weapons"], # Huntress
    ["heads", "bodies", "weapons"], # Cannibal
    ["heads", "bodies", "weapons"], # Nightmare
    ["masks", "bodies", "weapons"], # Pig
    ["heads", "bodies", "weapons"], # Clown
    ["heads", "bodies", "weapons"], # Spirit
    ["masks", "bodies", "weapons"], # Legion
    ["masks", "bodies", "weapons"], # Plague
    ["masks", "bodies", "weapons"], # Ghost Face
    ["heads", "bodies", "weapons"], # Demogorgon
    ["masks", "bodies", "weapons"], # Oni
    ["heads", "bodies", "weapons"], # Deathslinger
    ["heads", "bodies", "weapons"], # Executioner
    ["heads", "bodies", "weapons"], # Blight
    ["heads", "bodies", "weapons"], # Twins
    ["heads", "bodies", "weapons"], # Trickster
    ["heads", "bodies", "weapons"], # Nemesis
    ["heads", "bodies", "weapons"], # Cenobite
    ["heads", "bodies", "weapons"], # Artist
    ["heads", "bodies", "weapons"], # Onryo
    ["arms", "bodies", "weapons"], # Dredge
    ["heads", "bodies", "weapons"], # Mastermind
    ["heads", "bodies", "weapons"], # Knight
    ["heads", "bodies", "weapons"], # Skull Merchant
    ["heads", "bodies", "weapons"], # Singularity
    ["heads", "bodies", "weapons"], # Xenomorph
    ["heads", "bodies", "weapons"], # Good Guy
    ["heads", "bodies", "weapons"], # Unknown
    ["heads", "bodies", "weapons"], # Lich
    ["heads", "bodies", "weapons"], # Dark Lord
    ["heads", "bodies", "weapons"], # Houndmaster
    ["heads", "legs", "upperBodies"], # Ghoul
    ["heads", "bodies", "weapons"], # Animatronic
    ["heads", "bodies", "weapons"], # Krasue
    ["heads", "bodies", "weapons"] # First
]

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
        if character < len(killerCategoryMap):
            if category == "masks":
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

# Loads a single CustomizationItemDB.json file
def loadCustomizationItemDB(path):
    itemDB = []
    with open(path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        rows = data[0]["Rows"]
        for key, entry in rows.items():
            # Category
            category = entry["Category"]
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
                character = entry["AssociatedCharacter"]
                # 268435456 is the CharacterIndex of K01, so if AssociatedCharacter is greater than or equal to this value, the character is a killer
                killer = character >= 268435456
                if killer:
                    character -= 268435456
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
            category = item["category"]
            if not category in ids:
                ids[category] = 1
            item["id"] = ids[category]
            items[item["key"]] = item
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
        if "LocalizedString" in collectionName:
            # localizedString.lower().strip() gets rid of most duplicates, but some items refer to the same collection with different spelling or grammar...
            localizedString = collectionName["LocalizedString"].lower().strip()
            if localizedString in collections:
                collectionId = collections[localizedString]["id"]
            else:
                collectionId = len(collections) + 1
                collections[localizedString] = {
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