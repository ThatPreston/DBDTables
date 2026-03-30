from pathlib import Path
import os
import json
import Config
from utils import AssetDecryption

remoteContentCachePath = Path(os.getenv("LOCALAPPDATA")) / "DeadByDaylight/Saved/PersistentDownloadDir/RemoteContentCache/"

# Attempts to load and decrypt the desired backend file from %localappdata%/DeadByDaylight/Saved/PersistentDownloadDir/RemoteContentCache/
def loadFromRemoteContentCache(name, desiredVersion):
    path = remoteContentCachePath / name
    if path.is_file():
        branch = desiredVersion.split("_")[1]
        with open(path, "r") as inputFile:
            data = inputFile.read()
            decrypted, decryptedVersion = AssetDecryption.decryptAsset(data[4:], branch)
            return decrypted, decryptedVersion
    return None, None

# Attempts to load a backend file from the decrypted cache
def getFromDecryptedCache(version, name):
    path = Config.decryptedFilesPath / version / name
    if path.is_file():
        with open(path, "r", encoding = "utf-8") as f:
            return json.load(f)
    return None

def loadBackendFile(name, desiredVersion):
    # Check if the file exists in the decrypted cache
    cached = getFromDecryptedCache(desiredVersion, name)
    if cached is not None:
        return cached
    # If not, try loading and decrypting it from the remote content cache
    decryptedString, decryptedVersion = loadFromRemoteContentCache(name, desiredVersion)
    if decryptedString is not None:
        saveJson(Config.decryptedFilesPath / decryptedVersion, name, decryptedString)
        if decryptedVersion == desiredVersion:
            return json.loads(decryptedString)
        else:
            # This could happen if someone installs or updates the game but doesn't load in, leaving the remote content cache outdated
            print(f"Backend file \"{name}\" was decrypted from the remote content cache, but its version does not match the configured game version!")
            return None
    print(f"Backend file \"{name}\" could not be found or decrypted!")
    return None

def saveJson(directory, name, data):
    directory.mkdir(parents = True, exist_ok = True)
    with open(directory / name, "w", encoding = "utf-8", newline = "\n") as f:
        f.write(data)

def getTomeNames():
    tomes = []
    for i in range(22):
        tomeName = f"Tome{(i + 1):02d}"
        tomes.append(tomeName)
    return tomes