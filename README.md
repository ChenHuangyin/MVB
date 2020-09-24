# Program Instructions 

This instruction introduces the MVB program we implement.

## Running the program
To run our program, simply run the `driver.py` by using `python3 driver.py`, then all relevant tests will be executed and files will be generated. Also, the program will print out the test results in the terminal so we can monitor the tests conveniently.


## Code structure overview

`Block.py`

- *Block* class and *BlockTreeNode* class are implemented. *Block* class represents the basic structure of a block in the Blockchain. *BlockTreeNode* class is used to represent a node in the Merkle tree, which facilitates finding the previous block.

`Node.py`

- The *Node* class is implemented in this file. Each object of this class is a blockchain network node,  with ability to do verifications, broadcast mined blocks, mine blocks from Tx pools and manage files.

`Transaction.py`

- 3 classes related to transactions are implemented, including *TxInput*, *TxOutput* and *Transaction*.

`MVB.py`

- Implementation of a Blockchain network, including multiple nodes and a global transaction pool.

`MVBTest.py`

- Preparation for test cases, including generating genesis transaction. 
- Contains different test methods, each of which will read test input from corresponding transaction Json files. 

`Driver.py`

- Creates an object of MVBTest and calls all the test methods. Between different tests, we sleep for a random time up to 1 second.


## Design of tests

### Json files for test input
We design 7 different json files, each of which contains multiple transactions and these transactions will be used by different test methods in our `MVBTest.py` to cover different cases.

`GenesisTx.json`

- contains the genesis transaction with 15 initial outputs

`DoubleSpendTestTx.json`

- contains 2 transactions with the same input (so the first is valid but the second one is invalid)

`InputOutputSumTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has different input sum and output sum

`SigVerifyTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has the wrong signature  

`NumberHashTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has the wrong number hash

`TxInputsExistTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has non-exist input  

`PrevHashMatchTestTx.json`

- contains a valid transaction which will be used in prev-hash match test

`BlockPOWTestTx.json`

- contains a valid transaction which will be used in Block POW test

###  Explanation of test results

- "Block Verification Failed! Received block is already on the ledger"
    - Means that the received block is already on the ledger. E.g. Node(thread) A mines out a block and broadcasts to another node B, but the receiver node also mines out the same block before it receives from A.
- "Tx Verification Failed! This Tx is already on the ledger"
    - Means that the Tx in the global Tx pool is already in the ledger, when the node try to mine a block with that Tx, this error will occur.  E.g. Node A awakes and receives a new block from other node. After verification, this block is put into the ledger. Then Node A try to mine the same Tx from global Tx pool. However, this Tx is already in the ledger.

## Files generated
- `Node-x.json`
    - This json file records the ledger in node X. Each node should have their own copy of the blockchain ledger, so in this task we have 8 nodes and thus 8 node-x.json, each of which is essentially the same, except for those nodes who are inhonest.
- 8 transaction Json files for tests
    - 15 transactions in 8 different transaction Json files. Details explained in the *Design of tests* section above.



