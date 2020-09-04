from typing import List
import json
from nacl.signing import SignedMessage
from hashlib import sha256


class TxOutput:
    def __init__(self, value: int, pubKey):
        self.value = value
        self.pubKey = pubKey

    def toString(self) -> str:
        itemList = [str(self.value), self.pubKey]
        return ''.join(itemList)

    def isEqual(self, txOutput) -> bool:
        return txOutput.value == self.value and txOutput.pubKey == self.pubKey


class TxInput:
    def __init__(self, number: int, output: TxOutput):
        self.number = number
        self.output = output

    def toString(self) -> str:
        itemList = [str(self.number), str(self.output.value), self.output.pubKey]
        return ''.join(itemList)

    def isEqual(self, txInput) -> bool:
        return self.number == txInput.number and self.output.isEqual(txInput.output)


class Transaction:
    def __init__(self, txNumber: int, txInputs: List[TxInput], txOutputs: List[TxOutput], sig: SignedMessage):
        self.txNumber = txNumber
        self.txInputs = txInputs
        self.txOutputs = txOutputs
        self.sig = sig

    def getJson(self) -> json:
        jsonObj = {"number": self.txNumber}

        inputList = []
        for txInput in self.txInputs:
            txInputDict = {"number": self.txNumber, "output": {"value": txInput.output.value, "pubkey": str(txInput.output.pubKey)}}
            inputList.append(txInputDict)
        jsonObj["input"] = inputList

        outputList = []
        for txOutput in self.txOutputs:
            txOutputDict = {"value": txOutput.value, "pubkey": str(txOutput.pubKey)}
            outputList.append(txOutputDict)
        jsonObj["output"] = outputList

        jsonObj["sig"] = self.sig.signature

        return json.dumps(jsonObj)

    def getNumber(self):
        itemList = []
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(self.sig.signature)
        return sha256(''.join(itemList).encode('utf-8')).hexdigest()

    def getMessage(self):
        itemList = []
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        return (''.join(itemList)).encode('utf-8')

    def toString(self) -> str:
        itemList = [str(self.txNumber)]
        for txInput in self.txInputs:
            itemList.append(txInput.toString())
        for txOutput in self.txOutputs:
            itemList.append(txOutput.toString())
        itemList.append(self.sig.signature)
        return ''.join(itemList)

