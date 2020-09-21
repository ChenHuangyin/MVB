from BlockchainTest.MVBTest import *
import random

if __name__ == '__main__':
    Test1 = MVBTest(5, 15)  # MVBTest(nodes cnt, Keys cnt)

    Test1.doubleSpendTest()
    sleep(random.random())
    Test1.inputOutputSumTest()
    sleep(random.random())
    Test1.sigVerifyTest()
    sleep(random.random())
    Test1.numberHashTest()
    sleep(random.random())
    Test1.txInputsExistTest()


    # node1Json = Test1.mvb.networkNodes[0].getJson()
    # with open('node1.json', 'w', encoding='utf-8') as f:
    #     f.write(node1Json)
    # print(node1Json)
