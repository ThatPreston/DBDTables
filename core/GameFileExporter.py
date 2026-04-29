from pythonnet import load
import re
import sys
import Config
from utils import FileManager

load("coreclr")
import clr

sys.path.append(Config.librariesDir)
clr.AddReference(Config.librariesDir + "CUE4Parse.dll")

from CUE4Parse.FileProvider import DefaultFileProvider
from CUE4Parse.MappingsProvider import FileUsmapTypeMappingsProvider
from CUE4Parse.Compression import OodleHelper, ZlibHelper
from CUE4Parse.Encryption.Aes import FAesKey
from CUE4Parse.UE4.Localization import FTextLocalizationResource
from CUE4Parse.UE4.Versions import VersionContainer, EGame, ELanguage
from CUE4Parse.UE4.Objects.Core.Misc import FGuid
from UE4Config.Parsing import InstructionToken, InstructionType
from Newtonsoft.Json import JsonConvert, Formatting
from System.IO import DirectoryInfo, SearchOption
from System import StringComparer

provider = None
exportList = []

def getVersionContainer():
    version = tuple(map(int, Config.gameVersion.split("_")[0].split(".")))
    if version < (9, 6, 0):
        return VersionContainer(EGame.GAME_DeadByDaylight_Old)
    return VersionContainer(EGame.GAME_DeadByDaylight)

def init():
    global provider
    if provider is None:
        OodleHelper.Initialize(Config.librariesDir + OodleHelper.OODLE_NAME_CURRENT)
        ZlibHelper.Initialize(Config.librariesDir + ZlibHelper.DLL_NAME)
        provider = DefaultFileProvider(DirectoryInfo(Config.paksFolder), [], SearchOption.TopDirectoryOnly, getVersionContainer(), StringComparer.OrdinalIgnoreCase)
        provider.MappingsContainer = FileUsmapTypeMappingsProvider(Config.mappingFile)
        provider.Initialize()
        provider.SubmitKey(FGuid(0), FAesKey(Config.aesKey))
        provider.PostMount()
        provider.TryChangeCulture(provider.GetLanguageCode(ELanguage.English))

def readAccessKeys():
    if provider is None:
        raise Exception("File provider not initialized!")
    instructions = []
    for section in provider.DefaultGame.Sections:
        if section.Name == "/Script/AccessKeys.AccessKeys":
            for token in section.Tokens:
                if isinstance(token, InstructionToken) and token.Key == "AccessKeys":
                    instructions.append(token)
    keys = {}
    for instruction in instructions:
        if instruction.InstructionType == InstructionType.Add:
            keys.update(dict(re.findall(r'KeyId="([^"]+)",Key="([^"]+)"', instruction.Value)))
    return keys

def populateExportList():
    if provider is None:
        raise Exception("File provider not initialized!")
    exportList.clear()
    for file in provider.Files.Values:
        name = file.Name
        match name:
            case "CustomizationItemDB.uasset" | "OutfitDB.uasset":
                exportList.append(file)
            case "DeadByDaylight.locres":
                exportList.append(file)
    return len(exportList)

def exportFiles(step):
    if provider is None:
        raise Exception("File provider not initialized!")
    if len(exportList) > 0:
        for file in exportList:
            match file.Extension:
                case "uasset":
                    package = provider.LoadPackage(file)
                    FileManager.saveJson(Config.gameFilesPath / file.Directory, file.NameWithoutExtension + ".json", JsonConvert.SerializeObject(package.GetExports(), Formatting.Indented))
                case "locres":
                    locres = FTextLocalizationResource(file.CreateReader())
                    FileManager.saveJson(Config.gameFilesPath / file.Directory, file.NameWithoutExtension + ".json", JsonConvert.SerializeObject(locres, Formatting.Indented))
            step()