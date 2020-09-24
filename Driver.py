from BlockchainTest.MVBTest import *
import random

if __name__ == '__main__':
    # initialize a blockchain test network with 8 nodes
    Test = MVBTest(8)
    sleep(random.uniform(0.5, 1))

    Test.multipleValidTxTest()
    sleep(random.uniform(0.5, 1))

    Test.doubleSpendTest()
    sleep(random.uniform(0.5, 1))

    Test.inputOutputSumTest()
    sleep(random.uniform(0.5, 1))

    Test.sigVerifyTest()
    sleep(random.uniform(0.5, 1))

    Test.numberHashTest()
    sleep(random.uniform(0.5, 1))

    Test.txInputsExistTest()
    sleep(random.uniform(0.5, 1))

    Test.prevHashMatchTest()
    sleep(random.uniform(0.5, 1))

    Test.blockPOWTest()
