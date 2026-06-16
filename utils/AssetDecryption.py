from Crypto.Cipher import AES
import base64
import zlib
import Config

# All credit for these algorithms goes to Masusder

assetEncryptionPrefix = "DbdDAwAC"
zlibCompressionPrefix = "DbdDAQEB"

def decompress(text):
    if text.startswith(zlibCompressionPrefix):
        noPrefix = text[len(zlibCompressionPrefix):]
        decodedBytes = base64.b64decode(noPrefix)
        expectedLength = int.from_bytes(decodedBytes[:4], byteorder = "little")
        decompressed = zlib.decompress(decodedBytes[4:])
        if len(decompressed) != expectedLength:
            raise Exception("Decompression failed!")
        return decompressed.decode("utf-16")
    return text

def decryptSymmetrical(decodedBuffer, decryptedKey):
    cipher = AES.new(decryptedKey, AES.MODE_ECB)
    decryptedBytes = cipher.decrypt(bytearray(decodedBuffer))
    offsetBytes = []
    for i in range(len(decryptedBytes)):
        raw = decryptedBytes[i]
        if raw != 0:
            offset = (raw + 1) % 256
            offsetBytes.append(offset)
        else:
            break
    result = bytearray(offsetBytes).decode("ascii")
    return decompress(result)

def getKeyId(decodedBytes, length):
    keyIdBuffer = []
    for i in range(length):
        keyIdBuffer.append(decodedBytes[i] + 1)
    return "".join([chr(v) for v in keyIdBuffer]).replace("\u0001", "")

def decryptAsset(text, branch):
    if text.startswith(assetEncryptionPrefix):
        noPrefix = text[len(assetEncryptionPrefix):]
        decodedBytes = base64.b64decode(noPrefix)
        # Slice length consists of the version string, an underscore, the branch string, and a  character.
        # For example, "10.0.0_live" has a slice length of 12.
        # Generally, the version length doesn't change (though it did from 9.x.x -> 10.x.x) so we can just add 8 to the branch length for the same result.
        sliceLength = 8 + len(branch)
        resultKeyId = getKeyId(decodedBytes, sliceLength)
        if resultKeyId in Config.accessKeys:
            s3AccessKey = Config.accessKeys[resultKeyId].replace("-", "+").replace("_", "/")
            decryptedKey = base64.urlsafe_b64decode(s3AccessKey)
            decodedBuffer = []
            for i in range(len(decodedBytes) - sliceLength):
                decodedBuffer.append(decodedBytes[i + sliceLength])
            return decryptSymmetrical(decodedBuffer, decryptedKey), resultKeyId
        else:
            raise Exception(f"Decryption for version {resultKeyId} failed! Please add the corresponding access key to the config!")
    return text, None