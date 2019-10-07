import block
import struct
import pending_pool as pp
import ipaddress
import json
import config

### FOR JSON
def jsonDefault(OrderedDict):
    return OrderedDict.__dict__
### END JSON

class Blockchain():
	
	### FOR JSON
	def __repr__(self): 	
		return json.dumps(self, default=jsonDefault, indent=4)
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
	def add_record_as_data(self,_record):
		self.__dict__.update(_record.__dict__)
	def add_record_as_attr(self,_record):
		self.record = _record
	### END JSON


	def __init__(self):
		self.reward = 50
		self.ideal_time = 60
		self.real_time = 15
		self.max_hash = int("f" * 64, 16)
		self.bits = 0
		self.target = int("0000aaaaaaaaaaaaaaaa00000000000000000000000000000000000000000000", 16)
		self.diff = self.max_hash / self.target

		self.chain = []
		self.height = 0#= self.init_file('chain.pickle', 1)
		self.nodes = []#= self.init_file('node', 0)

	def genesis_block(self):
		new_block = block.Block(reward = self.reward)
		if new_block.error == True:
			return False
		new_block.mine(self.target)
		self.chain.append(new_block)
		pp.add_data(self, 'blockchain.pickle')
		return True

	def reCalcDiff(self):
		self.real_time = int(float(self.chain[0].timestamp) - float(self.chain[4].timestamp))
		if self.real_time in range (self.ideal_time - 3, self.ideal_time + 3):
			return 1
		if self.real_time <= 0:
			self.real_time = 1
		coef = self.calcCoeff()
		self.diff = self.diff * coef
		self.target = self.max_hash / self.diff 

	def calcCoeff(self):
		coef = self.ideal_time / self.real_time
		if coef > 1.25:
			return (1.25)
		if coef < 0.75:
			return (0.75)
		return (coef)

	def mine(self, prev_hash):
		self.height += 1
		new_block = block.Block(reward = self.reward, previous_hash = prev_hash, height = self.height)
		new_block.mine(self.target)
		self.chain.insert(0, new_block)
		config.broadcast_to_friend(new_block, '/block/new')
		pp.add_data(self, 'blockchain.pickle')
		if len(self.chain) % 5 == 0:
			self.reCalcDiff()
		if (len(self.chain) % 10 == 0):
			self.reward /= 2

	def add_node(self, node):
		ip = node.split(':')[0]
		try:
			ip = ipaddress.ip_address(ip)
		except ValueError:
			return(0)
		if int(node.split(':')[1]) >= 1 and int(node.split(':')[1]) <= 65535:
			# self.node.append(node)
			pp.add_node_to_file(node)
			return(1)
		else:
			return(0)

	def init_file(self, name, t):
		data = pp.get_data(name)
		if data == False:
			data = []
			height = 0
		else:
			data = json.loads(data)
			if t != 0:
				height = data.chain[0].height
		if t == 1:		
			return data, height
		else:
			return data

def fromBitsToDiff(bits):
	leng = int(bits[:2], 16)
	res = bits[2:]
	while (len(res) < leng * 2):
		res += "00"
	return (res)

def fromDiffToBits(diff):
	res = hex(len(diff) // 2)[2:]
	res += diff[0:6]
	return (res)
