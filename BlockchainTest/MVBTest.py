from BlockchainNetwork.MVB import *
from threading import Thread

coloredlogs.install()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class MVBTest:
    def __init__(self, initialNodeCnt, initialOutputCnt):
        self.mvb = MVB()
        self.signingKeysList = []
        self.pubKeysList = []
        self.pubKeysByteList = []
        self.__initialSigningKeys(initialOutputCnt)
        self.__initialPubKeys()

        self.mvb.generateGenesisBlock(self.pubKeysByteList)
        self.mvb.initialNodes(initialNodeCnt)

    def doubleSpendTest(self):
        """
            txOutputs is the genesis output.
            txOutputs[0] was used twice in this test.
            Both Tx1 and Tx2 make txOutputs[0] as input.
            When Tx2 is mined, the verification will be failed.
        """
        log.info("--------------------Double spend test now started-------------------")
        Tx1Inputs = [TxInput(self.mvb.genesisBlock.tx.txNumber, self.mvb.genesisBlock.tx.txOutputs[0])]
        Tx1Outputs = [TxOutput(500, self.pubKeysByteList[0]),
                      TxOutput(500, self.pubKeysByteList[1])]
        Tx1 = Transaction(0, Tx1Inputs, Tx1Outputs, None)
        Tx1.sign(self.signingKeysList[0])
        Tx1.calculateNumber()

        Tx2Inputs = [TxInput(1, self.mvb.genesisBlock.tx.txOutputs[0])]
        Tx2Outputs = [TxOutput(500, self.pubKeysByteList[2]),
                      TxOutput(500, self.pubKeysByteList[3])]
        Tx2 = Transaction(0, Tx2Inputs, Tx2Outputs, None)
        Tx2.sign(self.signingKeysList[0])
        Tx2.calculateNumber()
        # print(Tx1.calculateNumber())
        # self.mvb.txWaitingPool += [Tx1, Tx2]

        self.createTxJsonFile("DoubleSpendTestTx.json", [Tx1, Tx2])
        self.mvb.txWaitingPool += self.readTxFromFile('DoubleSpendTestTx.json')

        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def inputOutputSumTest(self):
        log.info("--------------------Input output sum test now started-------------------")
        ledger = self.mvb.networkNodes[0].ledger

        # sender is 1
        newTx3InputNumber = ledger[1].nowBlock.tx.txNumber
        newTx3InputOutput = ledger[1].nowBlock.tx.txOutputs[0]
        Tx3Inputs = [TxInput(newTx3InputNumber, newTx3InputOutput)]
        Tx3Outputs = [TxOutput(250, self.pubKeysByteList[0]),
                      TxOutput(250, self.pubKeysByteList[14])]

        Tx3 = Transaction(0, Tx3Inputs, Tx3Outputs, None)
        Tx3.sign(self.signingKeysList[0])
        Tx3.calculateNumber()

        # sender is 2
        newTx4InputNumber1 = ledger[0].nowBlock.tx.txNumber
        newTx4InputNumber2 = ledger[1].nowBlock.tx.txNumber
        # 1000 from genesis tx
        newTx4InputOutput1 = ledger[0].nowBlock.tx.txOutputs[1]
        # 500 from tx1
        newTx4InputOutput2 = ledger[1].nowBlock.tx.txOutputs[1]
        # input sum is 1500, output sum is 1400, invalid tx
        Tx4Inputs = [TxInput(newTx4InputNumber1, newTx4InputOutput1),
                     TxInput(newTx4InputNumber2, newTx4InputOutput2)]
        Tx4Outputs = [TxOutput(800, self.pubKeysByteList[4]),
                      TxOutput(600, self.pubKeysByteList[14])]

        Tx4 = Transaction(0, Tx4Inputs, Tx4Outputs, None)
        Tx4.sign(self.signingKeysList[1])
        Tx4.calculateNumber()

        self.mvb.txWaitingPool += [Tx3, Tx4]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def sigVerifyTest(self):
        log.info("--------------------Signature verify test now started-------------------")
        ledger = self.mvb.networkNodes[0].ledger

        # sender is 6
        newTx5InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx5InputOutput = ledger[0].nowBlock.tx.txOutputs[5]
        Tx5Inputs = [TxInput(newTx5InputNumber, newTx5InputOutput)]
        Tx5Outputs = [TxOutput(250, self.pubKeysByteList[5]),
                      TxOutput(750, self.pubKeysByteList[14])]

        Tx5 = Transaction(0, Tx5Inputs, Tx5Outputs, None)
        Tx5.sign(self.signingKeysList[5])
        Tx5.calculateNumber()

        # sender is 8
        newTx6InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx6InputOutput = ledger[0].nowBlock.tx.txOutputs[7]
        Tx6Inputs = [TxInput(newTx6InputNumber, newTx6InputOutput)]
        Tx6Outputs = [TxOutput(400, self.pubKeysByteList[7]),
                      TxOutput(600, self.pubKeysByteList[14])]

        Tx6 = Transaction(0, Tx6Inputs, Tx6Outputs, None)
        # invalid signature
        Tx6.sign(self.signingKeysList[6])
        Tx6.calculateNumber()

        self.mvb.txWaitingPool += [Tx5, Tx6]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def badStructureTest(self):
        pass

    def numberHashTest(self):
        log.info("--------------------Number hash test now started-------------------")
        ledger = self.mvb.networkNodes[0].ledger

        # sender is 6
        newTx5InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx5InputOutput = ledger[0].nowBlock.tx.txOutputs[4]
        Tx5Inputs = [TxInput(newTx5InputNumber, newTx5InputOutput)]
        Tx5Outputs = [TxOutput(250, self.pubKeysByteList[4]),
                      TxOutput(750, self.pubKeysByteList[5])]

        Tx5 = Transaction(0, Tx5Inputs, Tx5Outputs, None)
        Tx5.sign(self.signingKeysList[4])
        Tx5.calculateNumber()

        # sender is 8
        newTx6InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx6InputOutput = ledger[0].nowBlock.tx.txOutputs[13]
        Tx6Inputs = [TxInput(newTx6InputNumber, newTx6InputOutput)]
        Tx6Outputs = [TxOutput(400, self.pubKeysByteList[13]),
                      TxOutput(600, self.pubKeysByteList[14])]

        Tx6 = Transaction(0, Tx6Inputs, Tx6Outputs, None)
        Tx6.sign(self.signingKeysList[13])
        # wrong transaction number
        Tx6.txNumber = 1234

        self.mvb.txWaitingPool += [Tx5, Tx6]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def txInputsExistTest(self):
        log.info("--------------------Transaction inputs exist test now started-------------------")
        ledger = self.mvb.networkNodes[0].ledger

        # sender is 6
        newTx5InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx5InputOutput = ledger[0].nowBlock.tx.txOutputs[11]
        Tx5Inputs = [TxInput(newTx5InputNumber, newTx5InputOutput)]
        Tx5Outputs = [TxOutput(250, self.pubKeysByteList[11]),
                      TxOutput(750, self.pubKeysByteList[12])]

        Tx5 = Transaction(0, Tx5Inputs, Tx5Outputs, None)
        Tx5.sign(self.signingKeysList[11])
        Tx5.calculateNumber()

        # sender is 8
        newTx6InputNumber = ledger[0].nowBlock.tx.txNumber
        newTx6InputOutput = ledger[0].nowBlock.tx.txOutputs[7]
        Tx6Inputs = [TxInput(newTx6InputNumber, newTx6InputOutput)]
        Tx6Outputs = [TxOutput(400, self.pubKeysByteList[7]),
                      TxOutput(600, self.pubKeysByteList[6])]

        Tx6 = Transaction(0, Tx6Inputs, Tx6Outputs, None)
        Tx6.sign(self.signingKeysList[7])
        Tx6.calculateNumber()
        # non-exist input
        Tx6.txInputs[0].output.value = 333

        self.mvb.txWaitingPool += [Tx5, Tx6]
        self.mvb.broadcastTxPools()
        for i, node in enumerate(self.mvb.networkNodes):
            nodeThread = Thread(target=self.threadMining, args=(node, 1))
            nodeThread.start()

    def broadcastBlockTest(self):
        pass

    def threadMining(self, node: Node, i):
        # nowTime = time.time()
        # while True:
        #     node.receiveBroadcastBlock()
        #     for tx in node.globalTxPool:
        #         node.mineBlock(tx)
        #         node.globalTxPool.remove(tx)
        #     if time.time() - nowTime > 10:
        #         break
        for tx in node.globalTxPool:
            node.mineBlock(tx)
        node.globalTxPool = []
        node.saveToFile()

    def createTxJsonFile(self, FILENAME: str, txList: List[Transaction]):
        txListJsonObj = {'txList': []}
        for tx in txList:
            txListJsonObj['txList'].append(tx.getJsonObj())
        with open(FILENAME, 'w', encoding='utf-8') as f:
            f.write(json.dumps(txListJsonObj, indent=4))

    def readTxFromFile(self, FILENAME: str) -> List[Transaction]:
        txList = []
        with open(FILENAME, 'r', encoding='utf-8') as f:
            txListJsonObj = json.load(f)
        for txObj in txListJsonObj['txList']:
            newTx = Transaction(jsonObj=txObj)
            txList.append(newTx)
        return txList

    def __initialSigningKeys(self, cnt: int) -> None:
        """
            Generate and update signingKeys List for the network
        """
        for _ in range(cnt):
            self.signingKeysList.append(SigningKey.generate())
        log.info(str(cnt) + " signing keys have been generated successfully")
        # sleep(2)

    def __initialPubKeys(self):
        for signingKey in self.signingKeysList:
            verifyKey = signingKey.verify_key
            verifyKeyByte = verifyKey.encode(encoder=HexEncoder)
            self.pubKeysList.append(verifyKey)
            self.pubKeysByteList.append(verifyKeyByte)
        log.info(str(len(self.pubKeysList)) + " public keys have been generated successfully")
        # sleep(2)
