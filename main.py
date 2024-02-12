import time
import hashlib

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = ''.join([str(trans.to_dict()) for trans in self.transactions]) + str(self.previous_hash) + str(self.timestamp) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Node:
    def __init__(self, address, bandwidth):
        self.address = address
        self.bandwidth = bandwidth
        self.blockchain = Blockchain()
        self.pending_transactions = []

    def contribute_bandwidth(self, bandwidth):
        self.bandwidth += bandwidth

    def validate_transaction(self, transaction):
        # Validate transaction based on available bandwidth
        if self.bandwidth >= transaction.amount:
            return True
        return False

    def create_transaction(self, sender, receiver, amount):
        if self.validate_transaction(Transaction(sender, receiver, amount)):
            self.pending_transactions.append(Transaction(sender, receiver, amount))
            return True
        return False

    def mine_block(self, difficulty):
        if not self.pending_transactions:
            return False

        new_block = Block(self.pending_transactions, self.blockchain.get_last_block().hash)
        new_block.mine_block(difficulty)
        self.blockchain.add_block(new_block)
        self.pending_transactions = []
        return True

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Number of leading zeros required in the hash for proof-of-work

    def create_genesis_block(self):
        return Block([], '0')

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        self.chain.append(block)

    def is_valid_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def consensus(self, node):
        # Replace the chain with the longest valid chain in the network
        longest_chain = None
        max_length = len(self.chain)

        for neighbor in node.neighbors:
            length = len(neighbor.blockchain.chain)
            if length > max_length and neighbor.blockchain.is_valid_chain():
                max_length = length
                longest_chain = neighbor.blockchain.chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

# Example usage
node1 = Node("127.0.0.1", 100)  # Node with 100 Mbps bandwidth
node2 = Node("192.168.1.1", 50)  # Node with 50 Mbps bandwidth

# Node 1 creates and broadcasts a transaction
node1.create_transaction("Alice", "Bob", 10)
node1.mine_block(4)

# Node 2 joins the network and synchronizes the blockchain
node2.blockchain.chain = node1.blockchain.chain

# Node 2 contributes bandwidth and mines a block
node2.contribute_bandwidth(10)
node2.create_transaction("Bob", "Charlie", 5)
node2.mine_block(4)

# Node 1 and Node 2 reach consensus
node1.blockchain.consensus(node2)

# Both nodes now have the same blockchain
print("Node 1 Blockchain:", [block.hash for block in node1.blockchain.chain])
print("Node 2 Blockchain:", [block.hash for block in node2.blockchain.chain])

