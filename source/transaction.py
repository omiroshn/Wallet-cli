import hashlib
import binascii
import wallet
import codecs
import base58
import config
import bech32

OP_DUP = '76'
OP_HASH160 = 'a9'
OP_EQUALVERIFY = '88'
OP_CHECKSIG = 'ac'
SIGHASH_ALL = '01'

class Input():
	def __init__(self, prev_txid, vout, sign_key, script_sig = 1):
		self.prev_txid = get_lnf(prev_txid)
		self.vout = get_int_lnf(vout, 8)
		if script_sig == 1:
			self.sign_key = sign_key
			signature = binascii.hexlify(self.sign_key['sign']).decode()
			public_key = binascii.hexlify(self.sign_key['pub_key'].to_string()).decode()
			public_key = wallet.get_compressed_key('04' + public_key)
			len_pub_key = hex(int(len(public_key) / 2))[2:]
			len_signature = hex(int((len(signature) + len(SIGHASH_ALL))/ 2))[2:]
			self.script_sig = len_signature + signature + SIGHASH_ALL + len_pub_key + public_key
		else:
			self.script_sig = script_sig
		self.script_len = hex(int(len(self.script_sig) / 2))[2:]
		if (len(self.script_sig) < 2):
			self.script_len = '0' + self.script_len
		self.sequence = 'ffffffff'

	def input_concat(self):
		return self.prev_txid + self.vout + self.script_len + self.script_sig + self.sequence

	def get_input(self):
		data = {}
		data['txid'] = self.prev_txid
		data['vout'] = self.vout
		data['script_len'] = self.script_len
		data['script_sig'] = self.script_sig
		data['sequence'] = self.sequence
		return data
		
class Output():
	def __init__(self, value, recipient_addr, segwit = 0):
		self.value = get_int_lnf(value, 16)
		if segwit == 0:
			address_decode = binascii.hexlify(base58.b58decode(recipient_addr)).decode('utf-8')
			encrypted_key = address_decode[2:-8]
			len_pub_hash = hex(int(len(encrypted_key) / 2))[2:]
		# if segwit == 1:
		# 	address_decode, data = bech32.decode('tb', recipient_addr)
		# 	print("First param: %s\nSecond param")
		# 	len_pub_hash = hex(int(len(encrypted_key) / 2))[2:]
		self.script_pubkey = OP_DUP+OP_HASH160+len_pub_hash+encrypted_key+OP_EQUALVERIFY+OP_CHECKSIG
		self.script_len = hex(int(len(self.script_pubkey) / 2))[2:]

	def output_concat(self):
		return self.value + self.script_len + self.script_pubkey

	def get_output(self):
		output = {}
		output['value'] = self.value
		output['script_len'] = self.script_len
		output['script_pubkey'] = self.script_pubkey
		return output

class Transaction():
	def __init__(self, version, inputs, outputs, locktime):
		self.version = get_int_lnf(version, 8)
		self.sigwit = 0
		self.input_count = self.count_arg(inputs)
		self.inputs = []
		# if self.input_count == '01':
		# 	self.inputs.append(inputs)
		# else:
		for elem in inputs:
			self.inputs.append(elem)
		self.output_count = self.count_arg(outputs)
		self.outputs = []
		# if self.output_count == '01':
		# 	self.outputs.append(outputs)
		# else:
		for elem in outputs:
			self.outputs.append(elem)
		self.locktime = get_int_lnf(locktime, 8)

	def count_arg(self, data):
		if type(data) == list:
			count = len(data)
			count = hex(count)[2:]
			while len(count) != 2:
				count = '0' + count
		else:
			return '01'
		return count

	def transaction_hash_calculate(self):
		for elem in self.inputs:
			concat_inputs += elem.input_concat()
		for elem in self.outputs:
			concat_outpts += elem.output_concat()
		concate = self.version + self.input_count + self.concat_inputs + self.concat_outpts + self.locktime
		concate = bytes(concate, 'utf-8')
		con_hash = hashlib.sha256(concate).hexdigest()
		return(con_hash)

	def get_full_transaction(self):
		transaction = {}
		transaction['version'] = self.version
		transaction['input_count'] = self.input_count
		transaction['input'] = []
		for elem in self.inputs:
			transaction['input'].append(elem)
		transaction['output_count'] = self.output_count
		transaction['output'] = []
		for elem in self.outputs:
			transaction['output'].append(elem)
		transaction['locktime'] = self.locktime
		if self.sigwit == 1:
			transaction['marker'] = self.marker
			transaction['flag'] = self.flag
			transaction['witness'] = []
			for elem in self.witness:
				transaction['witness'].append(elem) 
		return transaction
		
class CoinbaseInput(Input):
	def __init__(self, height):
		self.prev_txid = '0'*64
		self.vout = 'f'*8
		self.height = get_int_lnf(height, 6)
		self.script_sig = '03' + self.height + '2f48616f4254432f53756e204368756e2059753a205a6875616e67205975616e2c2077696c6c20796f75206d61727279206d653f2f06fcc9cacc19c5f278560300'
		self.script_len = hex(int(len(self.script_sig) / 2))[2:]
		self.sequence = 'ffffffff'
		

class CoinbaseTransaction(Transaction):
	def __init__(self, height = 0, reward = 50):
		try:
			f = open('minerkey', 'r')
		except IOError:
			print("Create file mainerkey with WIF key!!")
			return
		private_key = wallet.WIF_to_key(f.read())
		inputik = []
		inputik.append(CoinbaseInput(height))
		bitcoin_address = wallet.get_bitcoin_address(private_key)
		# print("Bitcoin address ", bitcoin_address)
		output = []
		output.append(Output(reward * pow(10, 8), bitcoin_address))
		Transaction.__init__(self, 1, inputik, output, 0)
	
	def get_info(self):
		return Transaction.get_full_transaction(self)

def get_int_lnf(data, lens):
	if type(data) != int:
		data = int(data)
	data = hex(data)[2:]
	while len(data) != lens:
		data = '0' + data
	lnf = codecs.encode(codecs.decode(data, 'hex')[::-1], 'hex').decode()
	return(lnf)

def get_lnf(data):
	return codecs.encode(codecs.decode(data, 'hex')[::-1], 'hex').decode()
