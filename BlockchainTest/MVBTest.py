from BlockchainNetwork.MVB import *

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

    def __initialSigningKeys(self, cnt: int) -> None:
        """
            Generate and update signingKeys List for the network
        """
        for _ in range(cnt):
            self.signingKeysList.append(SigningKey.generate())
        log.info(str(cnt) + " signing keys have been generated successfully")

    def __initialPubKeys(self):
        for signingKey in self.signingKeysList:
            self.pubKeysList.append(signingKey.verify_key)
        for pubKey in self.pubKeysList:
            self.pubKeysByteList.append(pubKey.encode(encoder=HexEncoder))
        log.info(str(len(self.pubKeysList)) + " public keys have been generated successfully")
