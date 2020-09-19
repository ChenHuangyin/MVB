from typing import List
import json
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from hashlib import sha256


class TxOutput:
    def __init__(self, value: int = None, pubKey=None, jsonObj=None):
        if jsonObj:
            self.__createWithJsonObj(jsonObj)
            return
        self.value = value
        self.pubKey = pubKey

    def toString(self) -> str:
        itemList = [str(self.value), str(self.pubKey)]
        return ''.join(itemList)

    def isEqual(self, txOutput) -> bool:
        return txOutput.value == self.value and txOutput.pubKey == self.pubKey

    def __createWithJsonObj(self, txOutputJsonObj):
        self.value = int(txOutputJsonObj['value'])
        self.pubKey = txOutputJsonObj['pubkey']


class TxInput:
    def __init__(self, number=None, output: TxOutput = None, jsonObj=None):
        if jsonObj:
            self.__createWithJsonObj(jsonObj)
            return
        self.number = number
        self.output = output

    def toString(self) -> str:
        itemList = [str(self.number), str(self.output.value), str(self.output.pubKey)]
        return ''.join(itemList)

    def isEqual(self, txInput) -> bool:
        return self.number == txInput.number and self.output.isEqual(txInput.output)

    def __createWithJsonObj(self, txInputJsonObj):
        self.number = txInputJsonObj['number']
        self.output = TxOutput(txInputJsonObj['output'])


class Transaction:
    def __init__(self, txNumber: int = None, txInputs: List[TxInput] = None, txOutputs: List[TxOutput] = None, sig=None,
                 jsonObj: dict = None):
        if jsonObj:
            self.__createWithJsonObj(jsonObj)
            return
        self.txNumber = txNumber
        self.txInputs = txInputs
        self.txOutputs = txOutputs
        self.sig = sig

    def getJsonObj(self) -> dict:
        jsonObj = {"number": self.txNumber}
        inputList = []
        for txInput in self.txInputs:
            txInputDict = {"number": txInput.number,
                           "output": {"value": txInput.output.value, "pubkey": str(txInput.output.pubKey)}}
            inputList.append(txInputDict)
        jsonObj["input"] = inputList

        outputList = []
        for txOutput in self.txOutputs:
            txOutputDict = {"value": txOutput.value, "pubkey": str(txOutput.pubKey)}
            outputList.append(txOutputDict)

        jsonObj["output"] = outputList
        jsonObj["sig"] = self.sig

        return jsonObj

    def getJson(self) -> str:
        jsonObj = self.getJsonObj()
        return json.dumps(jsonObj, indent=4)

    def getNumber(self):
        itemList = []
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(self.sig)
        self.txNumber = sha256(''.join(itemList).encode('utf-8')).hexdigest()
        return self.txNumber

    def getMessage(self):
        itemList = []
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        return (''.join(itemList)).encode('utf-8')

    def sign(self, signingKey: SigningKey):
        msg = self.getMessage()
        self.sig = str(signingKey.sign(msg, encoder=HexEncoder).signature.hex())
        # verifyKey = signingKey.verify_key
        # verifyKey.verify(self.sig, encoder=HexEncoder)

    def toString(self) -> str:
        itemList = [str(self.txNumber)]
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(self.sig)
        return ''.join(itemList)

    def __createWithJsonObj(self, txJsonObj: dict):
        self.txNumber = txJsonObj['number']
        self.txInputs = []
        self.txOutputs = []
        self.sig = txJsonObj['sig']
        for inputJsonObj in txJsonObj['input']:
            self.txInputs.append(TxInput(jsonObj=inputJsonObj))

        for outputJsonObj in txJsonObj['output']:
            self.txOutputs.append(TxOutput(jsonObj=outputJsonObj))


