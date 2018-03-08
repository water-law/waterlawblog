import hashlib
import json
import requests
from time import time   # unix 时间戳
from urllib.parse import urlparse


class BlockChain(object):
    def __init__(self):
        self.chain = list()
        self.current_transactions = list()

        # 增加创世快
        self.new_block(previous_hash=1, proof=50)
        # 网络上的节点
        self.nodes = set()

    def register_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    def new_block(self, proof, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = list()
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })
        # 返回下一个待挖的矿中 ？？
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # "生成块的 SHA-256 hash值"
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        # 工作量证明
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # 工作量的内容
        guess = '{}{}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        # 验证当前区块链的有效性， 包括哈希值和工作量证明
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print('{}'.format(last_block))
            print('{}'.format(block))
            print("\n--------------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        # 达成一致性共识
        # 与当前节点相邻的节点的合法区块链中最长的保持一致
        # 共识算法解决冲突
        # 使用网络中最长的链.
        # :return: < bool > True
        # 如果链被取代, 否则为False
        neighbours = self.nodes
        max_length = len(self.chain)
        new_chain = None  # 临时存储临近临近节点中比当点节点长的合法区块链

        for node in neighbours:
            response = requests.get('http://{}/chain'.format(node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    # 将此区块链替换掉当前的区块链
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

"""
block = {
    'index': 1,  # 索引
    'timestamp': 1506057125.900785, # Unix时间戳
    'transactions': [  # 交易列表
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000, # 工作量证明
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" # 前一个区块的Hash值
}
"""