from BlockchainTest.MVBTest import *
from Blockchain.Transaction import *
from Blockchain.Block import *
from Blockchain.Node import *

if __name__ == '__main__':
    Test1 = MVBTest(8, 15)
    node1Json = Test1.mvb.networkNodes[0].getJson()
    with open('node1.json', 'w', encoding='utf-8') as f:
        f.write(node1Json)
    print(node1Json)

