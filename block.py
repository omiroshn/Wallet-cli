import config
import json
import tx_validator as tx
import merkle
from hashlib import sha256
import pending_pool
import time
import transaction
import serializer
import binascii
import utxo_set

def jsonDefault(OrderedDict):
    return OrderedDict.__dict__

class Block():
	def __repr__(self): 	
		return json.dumps(self, default=jsonDefault, indent=4)
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
	def add_record_as_data(self,_record):
		self.__dict__.update(_record.__dict__)
	def add_record_as_attr(self,_record):
		self.record = _record

	def __init__(self, reward, previous_hash = 0, height = 0):
		self.error = False
		self.height = height
		self.reward = reward
		self.transactions = []
		self.timestamp = time.time()
		self.nonce = 0
		self.previous_hash = previous_hash
		if previous_hash == 0:
			self.transactions = self.create_coinbase(0)
			if self.transactions == None:
				self.error = True
				return
		else:
			transactions = pending_pool.get_valid_transactions(3)
			if transactions != '1':
				self.transactions = transactions
			tx = self.create_coinbase(self.height, reward)
			if tx == None:
				return None
			self.transactions.insert(0, tx)
		if previous_hash == 0:
			first_hash = sha256(bytes(self.transactions, 'utf-8')).hexdigest()
			self.merkle = sha256(bytes(first_hash, 'utf-8')).hexdigest()
		else:
			tx = self.transactions
			self.merkle = merkle.create_merkle_tree(self.transactions)
			self.merkle = binascii.hexlify(self.merkle).decode('utf-8')
			self.transactions = tx
		self.get_hash()

	def create_coinbase(self, height, reward = 50):
		tx = transaction.CoinbaseTransaction(height, reward)
		try:
			tx = tx.get_info()
		except:
			return None
		ser_trans = serializer.Serializer.serializer(tx)
		dtx = serializer.Deserializer.deserializer(ser_trans, 1)
		first_hash = sha256(bytes(ser_trans, 'utf-8')).hexdigest()
		hash_tx = sha256(bytes(first_hash, 'utf-8')).hexdigest()
		utxo_set.add_to_pool(dtx, hash_tx)
		return ser_trans
	
	def get_hash(self):
		data_for_hash = bytes(str(self.timestamp) + str(self.nonce) + str(self.previous_hash) + str(self.transactions) + str(self.merkle), 'utf-8')
		self.hash = sha256(data_for_hash).hexdigest()

	def mine(self, diff):
		while int(self.hash, 16) > diff:
			self.nonce += 1
			self.get_hash()

	def print_info(self):
		print("Block info")
		print("timestamp =\t", self.timestamp)
		print("nonce =\t", self.nonce)
		print("previous_hash =\t", self.previous_hash)
		print("hash =\t", self.hash)
		print("transactions =\t", self.transactions)
		print("markle_root =\t", self.merkle)
