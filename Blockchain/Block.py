import json
from Blockchain import Transaction


class Block:
    def __init__(self, tx: Transaction, prev, nonce, pow):
        self.tx = tx  # <a single transaction>
        self.prev = prev  # <hash of the previous block>
        self.nonce = nonce  # <the nonce value, used for proof-of-work>
        self.pow = pow  # <the proof-of-work, a hash of the tx, prev, and nonce fields>

    def getJson(self):
        jsonObj = {"tx": self.tx.getJson(), "prev": self.prev, "nonce": self.nonce, "pow": self.pow}
        return json.dumps(jsonObj)