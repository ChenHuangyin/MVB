from typing import List
import json
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from hashlib import sha256


class TxOutput:
    def __init__(self, value: int, pubKey):
        self.value = value
        self.pubKey = pubKey

    def toString(self) -> str:
        itemList = [str(self.value), str(self.pubKey)]
        return ''.join(itemList)

    def isEqual(self, txOutput) -> bool:
        return txOutput.value == self.value and txOutput.pubKey == self.pubKey


class TxInput:
    def __init__(self, number: int, output: TxOutput):
        self.number = number
        self.output = output

    def toString(self) -> str:
        itemList = [str(self.number), str(self.output.value), str(self.output.pubKey)]
        return ''.join(itemList)

    def isEqual(self, txInput) -> bool:
        return self.number == txInput.number and self.output.isEqual(txInput.output)


class Transaction:
    def __init__(self, txNumber: int, txInputs: List[TxInput], txOutputs: List[TxOutput], sig):
        self.txNumber = txNumber
        self.txInputs = txInputs
        self.txOutputs = txOutputs
        self.sig = sig

    def getJsonObj(self) -> json:
        jsonObj = {"number": self.txNumber}

        inputList = []
        for txInput in self.txInputs:
            txInputDict = {"number": txInput.number, "output": {"value": txInput.output.value, "pubkey": str(txInput.output.pubKey)}}
            inputList.append(txInputDict)
        jsonObj["input"] = inputList

        outputList = []
        for txOutput in self.txOutputs:
            txOutputDict = {"value": txOutput.value, "pubkey": str(txOutput.pubKey)}
            outputList.append(txOutputDict)
        jsonObj["output"] = outputList

        jsonObj["sig"] = str(self.sig.signature.hex())

        return jsonObj

    def getNumber(self):
        itemList = []
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(str(self.sig.signature.hex()))
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
        self.sig = signingKey.sign(msg, encoder=HexEncoder)

        verifyKey = signingKey.verify_key
        verifyKey.verify(self.sig, encoder=HexEncoder)

    def toString(self) -> str:
        itemList = [str(self.txNumber)]
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(str(self.sig.signature.hex()))
        return ''.join(itemList)
