from BlockchainTest.MVBTest import *
import random

if __name__ == '__main__':
    Test1 = MVBTest(8)  # MVBTest(nodes cnt, Keys cnt)

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
