import hashlib
from decimal import Decimal
from time import time
from urllib.parse import urlparse

import requests

from .utils import dumps, do_process_pow, valid_proof

DIFFICULTY = 8


class Blockchain:
	def __init__(self):
		self.current_transactions = []
		self.chain = []
		self.peers = set()

		# Create the genesis block
		self.new_block(previous_hash='1', proof=100)

	def register_node(self, address):
		"""
		Add a new node to the list of nodes

		:param address: Address of the node
		"""

		parsed_url = urlparse(address)
		if parsed_url.netloc:
			self.peers.add(parsed_url.netloc)
		elif parsed_url.path:
			# Accepts an URL without scheme like '192.168.0.5:5000'.
			self.peers.add(parsed_url.path)
		else:
			raise ValueError('Invalid URL')

	def valid_chain(self, chain):
		"""
		Determine if a given blockchain is valid

		:param chain: A blockchain
		:return: True if valid, False if not
		"""

		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			#  print(f'{last_block}')
			#  print(f'{block}')
			#  print("\n-----------\n")
			# Check that the hash of the block is correct
			last_block_hash = self.hash(last_block)
			if block['previous_hash'] != last_block_hash:
				return False

			# Check that the Proof of Work is correct
			if not valid_proof(last_block['proof'], block['proof'], last_block_hash, DIFFICULTY):
				return False

			last_block = block
			current_index += 1

		return True

	def resolve_conflicts(self):
		"""
		This is our consensus algorithm, it resolves conflicts
		by replacing our chain with the longest one in the network.

		:return: True if our chain was replaced, False if not
		"""

		new_chain = None

		# We're only looking for chains longer than ours
		max_length = len(self.chain)

		# Grab and verify the chains from all the peers in our network
		for node in self.peers:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				# Check if the length is longer and the chain is valid
				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain

		# Replace our chain if we discovered a new, valid chain longer than ours
		if new_chain:
			self.chain = new_chain
			return True

		return False

	def new_block(self, proof, previous_hash):
		"""
		Create a new Block in the Blockchain

		:param proof: The proof given by the Proof of Work algorithm
		:param previous_hash: Hash of previous Block
		:return: New Block
		"""

		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		self.current_transactions = []
		self.chain.append(block)

		return block

	def broadcast_transaction(self, transaction):
		for node in self.peers:
			response = requests.post(
				f'http://{node}/transactions',
				data=dumps(transaction, separators=(",", ":")),
				headers={'content-type': 'application/json'},
			)

			if response.status_code != 202:
				print(f'Failed to send transaction to node {node}', response)

	def new_transaction(self, sender, recipient, amount, timestamp=None, mine=False):
		"""
		Creates a new transaction to go into the next mined Block

		:param sender: Address of the Sender
		:param recipient: Address of the Recipient
		:param amount: Amount
		:return: The index of the Block that will hold this transaction
		"""
		transaction = {
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
			'timestamp': timestamp or time(),
		}
		if transaction not in self.current_transactions:
			self.current_transactions.append(transaction)
			print(f'added transaction to list {mine}')
			if not mine:
				self.broadcast_transaction(transaction)

	@property
	def last_block(self):
		return self.chain[-1]

	@staticmethod
	def hash(block):
		"""
		Creates a SHA-256 hash of a Block

		:param block: Block
		"""
		block_string = dumps(block, separators=(",", ":"), sort_keys=True).encode()

		return hashlib.sha256(block_string).hexdigest()

	def proof_of_work(self, last_block):
		"""
		Simple Proof of Work Algorithm:

			- Find a number p' such that hash(pp') contains leading DIFFICULTY zeroes
			- Where p is the previous proof, and p' is the new proof

		:param last_block: <dict> last Block
		:return: <int>
		"""

		last_proof = last_block['proof']
		last_hash = self.hash(last_block)

		return do_process_pow(last_proof, last_hash, DIFFICULTY)

	def get_balance(self, identifier):
		"""
		Returns the balance of a node, by iterating through all transactions

		:param identifier: <str> node identifier
		:return: <int> balance of the node
		"""
		if not self.valid_chain(self.chain):
			return None

		balance = Decimal(0)
		for block in self.chain:
			for transaction in block['transactions']:
				if transaction['sender'] == identifier:
					balance -= transaction['amount']
				if transaction['recipient'] == identifier:
					balance += transaction['amount']

		return balance
