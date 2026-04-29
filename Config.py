from pathlib import Path
import json
import sys
import os

rootDir = os.path.dirname(sys.argv[0])
librariesDir = rootDir + "/libraries/"

rootPath = Path(rootDir)
outputPath = rootPath / "output"
gameFilesPath = rootPath / "files/game"
decryptedFilesPath = rootPath / "files/decrypted"

def load():
    path = rootPath / "config.json"
    if path.is_file():
        with open(path, "r", encoding = "utf-8") as f:
            return json.load(f)
    # Default Config
    return {
        "gameVersion": "9.6.0_live",
        "paksFolder": "",
        "mappingFile": "",
        "enabledLanguages": ["de", "en", "es", "es-MX", "fr", "it", "ja", "ko", "pl", "pt-BR", "ru", "th", "tr", "zh-Hans", "zh-Hant"],
        "aesKey": "0x22b1639b548124925cf7b9cbaa09f9ac295fcf0324586d6b37ee1d42670b39b3",
        "accessKeys": {}
    }

configFile = load()

version = "1.0.3"
gameVersion = configFile["gameVersion"]
paksFolder = configFile["paksFolder"]
mappingFile = configFile["mappingFile"]
enabledLanguages = configFile["enabledLanguages"]
aesKey = configFile["aesKey"]
accessKeys = configFile["accessKeys"]

def save():
    data = {
        "gameVersion": gameVersion,
        "paksFolder": paksFolder,
        "mappingFile": mappingFile,
        "enabledLanguages": enabledLanguages,
        "aesKey": aesKey,
        "accessKeys": accessKeys
    }
    with open(Path(rootPath) / "config.json", "w", encoding = "utf-8") as f:
        json.dump(data, f, indent = "\t")