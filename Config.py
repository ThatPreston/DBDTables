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
    with open(Path(rootPath) / "config.json", "r", encoding = "utf-8") as f:
        return json.load(f)

configFile = load()

version = "1.0.0"
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