from typing import List
import json
from nacl.signing import SignedMessage


class TxOutput:
    def __init__(self, value: int, pubKey):
        self.value = value
        self.pubKey = pubKey


class TxInput:
    def __init__(self, number: int, output: TxOutput):
        self.number = number
        self.output = output


class Transaction:
    def __init__(self, txNumber: int, txInputs: List[TxInput], txOutputs: List[TxOutput], sig: SignedMessage):
        self.txNumber = txNumber
        self.txInputs = txInputs
        self.txOutputs = txOutputs
        self.sig = sig

    def getJson(self):
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