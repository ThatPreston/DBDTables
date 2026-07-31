from pathlib import Path
import json
import sys
import os
import copy

rootDir = os.path.dirname(sys.argv[0])
librariesDir = rootDir + "/libraries/"

rootPath = Path(rootDir)
outputPath = rootPath / "output"
gameFilesPath = rootPath / "files/game"
decryptedFilesPath = rootPath / "files/decrypted"
persistentDownloadDirPath = Path(os.getenv("LOCALAPPDATA")) / "DeadByDaylight/Saved/PersistentDownloadDir"

version = "1.0.7"

defaultConfig = {
    "gameVersion": "10.0.1_live",
    "paksFolder": "",
    "mappingFile": "",
    "enabledLanguages": ["de", "en", "es", "es-MX", "fr", "it", "ja", "ko", "pl", "pt-BR", "ru", "th", "tr", "zh-Hans", "zh-Hant"],
    "accessKeys": {},
    "extraFiles": []
}

def load():
    template = copy.deepcopy(defaultConfig)
    path = rootPath / "config.json"
    file = None
    if path.is_file():
        with open(path, "r", encoding = "utf-8") as f:
            try:
                file = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Failed to load config.json: {e}")
    if file is not None and isinstance(file, dict):
        for key, value in file.items():
            if key in template and isinstance(value, type(template[key])):
                template[key] = value
    return template

configFile = load()

gameVersion = configFile["gameVersion"]
paksFolder = configFile["paksFolder"]
mappingFile = configFile["mappingFile"]
enabledLanguages = configFile["enabledLanguages"]
accessKeys = configFile["accessKeys"]
extraFiles = configFile["extraFiles"]

def save():
    # Apply any changes to literal values
    configFile["gameVersion"] = gameVersion
    configFile["paksFolder"] = paksFolder
    configFile["mappingFile"] = mappingFile
    with open(Path(rootPath) / "config.json", "w", encoding = "utf-8") as f:
        json.dump(configFile, f, indent = "\t")