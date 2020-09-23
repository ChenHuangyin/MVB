from BlockchainTest.MVBTest import *
import random

if __name__ == '__main__':
    Test1 = MVBTest(2, 15)  # MVBTest(nodes cnt, Keys cnt)

    Test1.doubleSpendTest()
    sleep(random.uniform(0.5, 1))
    Test1.inputOutputSumTest()
    sleep(random.uniform(0.5, 1))
    Test1.sigVerifyTest()
    sleep(random.uniform(0.5, 1))
    Test1.numberHashTest()
    sleep(random.uniform(0.5, 1))
    Test1.txInputsExistTest()
    sleep(random.uniform(0.5, 1))
    Test1.prevHashMatchTest()
    sleep(random.uniform(0.5, 1))
    Test1.blockPOWTest()


    # node1Json = Test1.mvb.networkNodes[0].getJson()
    # with open('node1.json', 'w', encoding='utf-8') as f:
    #     f.write(node1Json)
    # print(node1Json)
