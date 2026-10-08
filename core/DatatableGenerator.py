from datetime import datetime
import json
import copy
import Config
from core import GameFileParser, CatalogParser, RiftParser, Localization
from utils import FileManager, LuaSerializer

saveDebugFiles = False

def localize(sortedItems, outfitsList, collectionsList, language, header):
    if not Localization.isCultureLoaded(language):
        print(f"No locres file found for {language}! Skipping...")

    fileExtension = "_" + language + ".lua"

    localizedItems = copy.deepcopy(sortedItems)
    localizedOutfits = copy.deepcopy(outfitsList)
    localizedCollections = copy.deepcopy(collectionsList)

    # Replace names and descriptions with localized strings
    for category, items in localizedItems.items():
        for item in items:
            item["name"] = Localization.getBestString(item["name"], language)
            item["desc"] = Localization.getBestString(item["desc"], language)
    for outfit in localizedOutfits:
        if not "fakeOutfit" in outfit:
            outfit["name"] = Localization.getBestString(outfit["name"], language)
            outfit["desc"] = Localization.getBestString(outfit["desc"], language)
    for collection in localizedCollections:
        collection["name"] = Localization.getBestString(collection["name"], language)

    # Add collections to the items table
    localizedItems["collections"] = localizedCollections

    # Save cosmetic pieces (serialized individually for formatting reasons)
    piecesResult = ""
    for category, items in localizedItems.items():
        categorySerialized = LuaSerializer.serialize(items, False, 1, 0)
        piecesResult += f"\n\np.{category} = {categorySerialized}"
    with open(Config.outputPath / ("cosmetic_pieces" + fileExtension), "w", encoding = "utf-8") as f:
        f.write(header + piecesResult + "\n\nreturn p")

    # Save outfits
    outfitsSerialized = LuaSerializer.serialize(localizedOutfits, False, 1, 0)
    with open(Config.outputPath / ("outfits" + fileExtension), "w", encoding = "utf-8") as f:
        f.write(header + "\n\np.outfits = " + outfitsSerialized + "\n\nreturn p")

def generate(setStatus):
    setStatus("Loading localization files...")
    Localization.load()

    setStatus("Loading game files...")
    items, outfits, collections = GameFileParser.parse()

    # Sort items into their categories
    sortedItems = {}
    for key, item in items.items():
        category = item["category"]
        if not category in sortedItems:
            sortedItems[category] = []
        sortedItems[category].append(item)

    # Append data from backend files
    catalogAppended = CatalogParser.appendData(items, outfits)
    if not catalogAppended:
        setStatus("Failed to load catalog!")
        return False
    riftsAppended = RiftParser.appendData(items, outfits)
    if not riftsAppended:
        setStatus("Failed to load rifts!")
        return False

    usedItems = GameFileParser.addCrossReferences(items, outfits)

    # Add fake outfits for all unused items
    for itemKey, item in items.items():
        if not item["category"] in GameFileParser.universalCategories:
            if not itemKey in usedItems:
                outfit = {
                    "id": len(outfits) + 1,
                    "rarity": item["rarity"],
                    "fakeOutfit": True,
                    "pieces": {item["category"]: item["id"]}
                }
                if "collectionId" in item:
                    outfit["collectionId"] = item["collectionId"]
                outfit["purchasable"] = item.get("purchasable", False)
                role = "killer" if "killer" in item else "survivor"
                outfit[role] = item[role]
                outfits[itemKey] = outfit

    outfitsList = list(outfits.values())
    collectionsList = list(collections.values())

    if saveDebugFiles:
        # Save files with extra data for debugging
        FileManager.saveJson(Config.outputPath, "cosmetic_pieces_debug.json", json.dumps(sortedItems, indent = "\t"))
        FileManager.saveJson(Config.outputPath, "outfits_debug.json", json.dumps(outfitsList, indent = "\t"))

    # Delete extra data
    for category, items in sortedItems.items():
        for item in items:
            del item["key"]
            del item["category"]
            # Survivor/killer is only needed for outfits
            if "survivor" in item:
                del item["survivor"]
            if "killer" in item:
                del item["killer"]
    for outfit in outfitsList:
        if not "fakeOutfit" in outfit:
            del outfit["key"]

    header = ""
    headerPath = Config.rootPath / "datatable_header.lua"
    if headerPath.is_file():
        with open(headerPath, "r", encoding = "utf-8") as headerFile:
            header += headerFile.read()
    header += "\n\n--Timestamp: " + str(datetime.now())
    header += "\n--Version: " + Config.version
    header += "\n--Game Version: " + Config.gameVersion

    Config.outputPath.mkdir(exist_ok = True)
    for language in Config.enabledLanguages:
        setStatus(f"Localizing to {language}...")
        localize(sortedItems, outfitsList, collectionsList, language, header)

    return True