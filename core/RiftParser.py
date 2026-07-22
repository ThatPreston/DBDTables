import Config
from utils import FileManager

tracks = ["free", "premium"]

# Set tome/riftPass, tier, and track values for an item or outfit
def assignData(items, outfits, key, riftType, riftNumber, tier, track):
    if key in items:
        item = items[key]
        item[riftType] = riftNumber
        item["tier"] = tier
        item["track"] = track
    elif key in outfits:
        outfit = outfits[key]
        outfit[riftType] = riftNumber
        outfit["tier"] = tier
        outfit["track"] = track
        for itemKey in outfit["pieces"]:
            if itemKey in items:
                item = items[itemKey]
                item[riftType] = riftNumber
                item["tier"] = tier
                item["track"] = track

# If an outfit has no tome/riftPass value but one of its pieces does, the outfit should also have it
def assignFromPieces(outfit, items):
    for itemKey in outfit["pieces"]:
        if itemKey in items:
            item = items[itemKey]
            if "tome" in item:
                outfit["tome"] = item["tome"]
                outfit["track"] = item["track"]
                return True
            elif "riftPass" in item:
                outfit["riftPass"] = item["riftPass"]
                outfit["track"] = item["track"]
                return True
    return False

def parseTierData(tierData, items, outfits, riftType, riftNumber):
    tierId = tierData["tierId"]
    for track in tracks:
        if track in tierData:
            for reward in tierData[track]:
                if reward["type"] == "inventory":
                    assignData(items, outfits, reward["id"], riftType, riftNumber, tierId, track)

# Reads tome and rift pass files and appends data to the cosmetic tables
def appendData(items, outfits):
    # Load Tomes
    for i, tomeName in enumerate(FileManager.getTomeNames()):
        tomeNumber = i + 1
        tomeData = FileManager.loadBackendFile("archiveRewardGrid_" + tomeName + ".json", Config.gameVersion)
        if tomeData is None:
            return False
        for tierData in tomeData[tomeName]["tierInfo"]:
            parseTierData(tierData, items, outfits, "tome", tomeNumber)

    # Load Rift Passes
    riftPasses = FileManager.loadBackendFile("challengeRewardTrackers.json", Config.gameVersion)
    if riftPasses is None:
        return False
    for passId, passData in riftPasses.items():
        passNumber = int(passId.split("_")[1])
        for tierData in passData["tierInfo"]:
            parseTierData(tierData, items, outfits, "riftPass", passNumber)

    for outfit in outfits.values():
        if (not "tome" in outfit) and (not "riftPass" in outfit):
            assignFromPieces(outfit, items)

    return True