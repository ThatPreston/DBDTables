from datetime import datetime
import json
import copy
import Config
from core import GameFileParser, CatalogParser, RiftParser
from utils import FileManager, LuaSerializer

saveDebugFiles = False

locresPath = Config.gameFilesPath / "DeadByDaylight/Content/Localization/DeadByDaylight"
locresCache = {}

def getLocres(language):
    if language in locresCache:
        return locresCache[language]
    path = locresPath / language / "DeadByDaylight.json"
    if path.is_file():
        with open(path, "r", encoding = "utf-8") as f:
            locres = json.load(f)
            locresCache[language] = locres
            return locres
    return None

def getLocalizedString(locres, tableId, key):
    if tableId in locres:
        return locres[tableId].get(key)
    return None

def getBestString(data, locres):
    # First check if namespace and key yields a translation
    namespace = data.get("Namespace")
    key = data.get("Key")
    if (namespace is not None) and (key is not None):
        translation = getLocalizedString(locres, namespace, key)
        if translation is not None:
            return translation.strip()
    # Some newer cosmetics use "TableId" instead of "Namespace"
    tableId = data.get("TableId")
    if (tableId is not None) and (key is not None):
        translation = getLocalizedString(locres, tableId.split(".")[-1], key)
        if translation is not None:
            return translation.strip()
    # Use LocalizedString if it exists
    localizedString = data.get("LocalizedString")
    if localizedString is not None:
        print(f"No translation found for source string \"{data.get("SourceString")}\"\nUsing localized (en) string: \"{localizedString}\"")
        return localizedString.strip()
    return "N/A"

def localize(sortedItems, outfitsList, collectionsList, language, header):
    locres = getLocres(language)
    if locres is None:
        print(f"No locres file found for {language}! Skipping...")

    fileExtension = "_" + language + ".lua"

    localizedItems = copy.deepcopy(sortedItems)
    localizedOutfits = copy.deepcopy(outfitsList)
    localizedCollections = copy.deepcopy(collectionsList)

    # Replace names and descriptions with localized strings
    for category, items in localizedItems.items():
        for item in items:
            item["name"] = getBestString(item["name"], locres)
            item["desc"] = getBestString(item["desc"], locres)
    for outfit in localizedOutfits:
        if not "fakeOutfit" in outfit:
            outfit["name"] = getBestString(outfit["name"], locres)
            outfit["desc"] = getBestString(outfit["desc"], locres)
    for collection in localizedCollections:
        collection["name"] = getBestString(collection["name"], locres)

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
    locresCache.clear()

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