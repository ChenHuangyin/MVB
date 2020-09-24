# Blockchains & Cryptocurrencies JHU 601.641

This project is a simulation of a "Minimum Viable Blockchain" (MVB), a simplified version of the technology underlying Bitcoin.

# Program Instructions 

## Code structure overview

## Design of tests
We design 8 different json files, each of which contains multiple transactions and these transactions will be used by different test methods in our `MVBTest.py` to cover different cases.
1. `GenesisTx.json`: contains the genesis transaction with 15 initial outputs
2. `DoubleSpendTestTx.json`: contains 2 transactions with the same input (so the first is valid but the second one is invalid)
3. `InputOutputSumTestTx.json`: contains 2 transactions, the first is valid while the second transaction has different input sum and output sum
4. `SigVerifyTestTx.json`: contains 2 transactions, the first is valid while the second transaction has the wrong signature  
5. `NumberHashTestTx.json`: contains 2 transactions, the first is valid while the second transaction has the wrong number hash
6. `TxInputsExistTestTx.json`: contains 2 transactions, the first is valid while the second transaction has non-exist input  
7. `PrevHashMatchTestTx.json`: contains a valid transaction which will be used in prev-hash match test
8. `BlockPOWTestTx.json`: contains a valid transaction which will be used in Block POW test

## Running the program
To run our program, simply run the `driver.py` by using `python3 driver.py`, then all relevant tests will be executed and files will be generated. Also, the program will print out the test results in the terminal so we can monitor the tests conveniently.

## Files generated
- `Node-x.json`
    - This json file records the ledger in node X. Each node should have their own copy of the blockchain ledger, so in this task we have 8 nodes and thus 8 node-x.json, each of which is essentially the same, except for those nodes who are inhonest.
- transaction file

## What we realized



