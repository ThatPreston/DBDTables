import Config
import json

exportsPath = Config.gameFilesPath / "DeadByDaylight"
locresPath = Config.gameFilesPath / "DeadByDaylight/Content/Localization/DeadByDaylight"

locresCache = {}

def isCultureLoaded(culture):
    return culture in locresCache

# Loads all .locres files and appends additional translations from LocalizedTexts.json files
def load():
    locresCache.clear()

    for culture in Config.enabledLanguages:
        path = locresPath / culture / "DeadByDaylight.json"
        if path.is_file():
            with open(path, "r", encoding = "utf-8") as f:
                locres = json.load(f)
                locresCache[culture] = locres

    for path in sorted(exportsPath.rglob("LocalizedTexts.json")):
        data = None
        try:
            with open(path, "r", encoding = "utf-8") as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            # There are some malformed empty LocalizedTexts.json files, just ignore them
            pass

        if data is not None:
            entries = data["allLocalizedText"]
            for entry in entries:
                namespace = entry["namespace"]
                key = entry["key"]

                for translation in entry["translations"]:
                    culture = translation["culture"]
                    locres = locresCache.get(culture)
                    if locres is not None:
                        namespaceDict = locres.setdefault(namespace, {})
                        namespaceDict[key] = translation["sourceString"]

def getLocalizedString(culture, tableId, key):
    locres = locresCache.get(culture)
    if locres is not None:
        if tableId in locres:
            return locres[tableId].get(key)
    return None

def getBestString(data, culture):
    # First check if namespace and key yields a translation
    namespace = data.get("Namespace")
    key = data.get("Key")
    if (namespace is not None) and (key is not None):
        translation = getLocalizedString(culture, namespace, key)
        if translation is not None:
            return translation.strip()

    # Some newer cosmetics use "TableId" instead of "Namespace"
    tableId = data.get("TableId")
    if (tableId is not None) and (key is not None):
        translation = getLocalizedString(culture, tableId.split(".")[-1], key)
        if translation is not None:
            return translation.strip()

    # Use LocalizedString if it exists
    localizedString = data.get("LocalizedString")
    if localizedString is not None:
        print(f"No translation found for source string \"{data.get("SourceString")}\"\nUsing localized (en) string: \"{localizedString}\"")
        return localizedString.strip()

    return None