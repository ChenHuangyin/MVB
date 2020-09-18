from Blockchain.Transaction import *
from Blockchain.Node import *
from time import sleep

coloredlogs.install()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class MVB:
    def __init__(self):
        log.info("Start initialling the MVB")
        # sleep(2)
        self.txWaitingPool: List[Transaction] = []
        self.networkNodes: List[Node] = []
        self.genesisBlock = None
        log.info("Initial success")
        # sleep(2)

    def initialNodes(self, cnt: int):
        for blockId in range(1, cnt + 1):
            newNode = Node(self.genesisBlock, str(blockId))
            self.networkNodes.append(newNode)
        for node in self.networkNodes:
            node.allNodeList += self.networkNodes
        log.info(str(cnt) + " network nodes have been set up successfully")
        # sleep(2)

    def generateGenesisBlock(self, pubKeysByteList: List[TxOutput]) -> None:
        """
            Generate the genesis Block
        """
        genesisTx = self.__generateGenesisTx(pubKeysByteList)
        genesisPrev = sha256("arbitrary data".encode('utf-8')).hexdigest()
        genesisNonce = 0
        genesisPow = 0
        self.genesisBlock = Block(genesisTx, genesisPrev, genesisNonce, genesisPow)
        log.info("Genesis block have been generated successfully")
        # sleep(2)

    def broadcastTxPools(self):
        for node in self.networkNodes:
            node.globalTxPool += self.txWaitingPool
        self.txWaitingPool = []

    def __generateGenesisTx(self, pubKeysByteList: List[TxOutput]) -> Transaction:
        """
            Generate the genesis Transaction
        """
        genesisTxOutputList = self.__generateGenesisTxOutputList(pubKeysByteList)
        genesisSigningKey = SigningKey.generate()
        genesisTx = Transaction(1, [], genesisTxOutputList, genesisSigningKey.sign('arbitrary msg'.encode("utf-8")))
        return genesisTx

    def __generateGenesisTxOutputList(self, pubKeysByteList: List[TxOutput]) -> List[TxOutput]:
        genesisTxOutputList = []
        for pubKeyByte in pubKeysByteList:
            genesisTxOutputList.append(TxOutput(1000, pubKeyByte))
        return genesisTxOutputList
