from pythonds.basic.stack import Stack
import wallet
import codecs
import ecdsa
import binascii
import serializer
import utxo_set as u
from copy import deepcopy
from hashlib import sha256
import wallet
import transaction as txid

OP_DUP = '76'
OP_HASH160 = 'a9'
OP_EQUALVERIFY = '88'
OP_CHECKSIG = 'ac'

def get_useful_data(unlocking_script, locking_script, transaction):
	data = {}
	len_sig = int(unlocking_script[:2], 16) * 2
	data['sig'] = unlocking_script[2:len_sig]
	data['pubkey'] = unlocking_script[4+len_sig:]
	data['DUP'] = locking_script[:2]
	data['HASH160'] = locking_script[2:4]
	len_key = int(locking_script[4:6], 16) * 2
	data['encr_pubkey'] = locking_script[6:6+len_key]
	i = 6+len_key
	data['EQUALVERIFY'] = locking_script[i:i+2]
	data['CHECKSIG'] = locking_script[i+2:i+4]
	# print(data)
	return verify_script(data, transaction)

def do_dup(s):
	new_one = s.peek()
	s.push(new_one)
	return s

def do_hash(s):
	elem = s.pop()
	hash_pubkey = wallet.encrypting_pubkey(elem)[2:]
	s.push(hash_pubkey)
	return s

def do_equalverify(s):
	elem1 = s.pop()
	elem2 = s.pop()
	if elem1 == elem2:
		return True
	else:
		return False

def getFullPubKeyFromCompressed(comp_key:  bytearray):
        x = int.from_bytes(comp_key[1:], byteorder='big')
        is_even = True if comp_key[1] == '2' else False
        """ Derive y point from x point """
        curve = ecdsa.SECP256k1.curve
        # The curve equation over F_p is:
        #   y^2 = x^3 + ax + b
        a, b, p = curve.a(), curve.b(), curve.p()
        alpha = (pow(x, 3, p) + a * x + b) % p
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, p)
        if (beta % 2) == is_even:
            beta = p - beta
        return bytearray.fromhex( f"04{x:064x}{beta:064x}")

def do_checksig(s, message):
	compressed_pubkey = bytearray.fromhex(s.pop())
	pubkey = getFullPubKeyFromCompressed(compressed_pubkey)
	sig = s.pop()
	sig = codecs.decode(sig, 'hex')
	vk = ecdsa.VerifyingKey.from_string(pubkey[1:], curve=ecdsa.SECP256k1)
	try:
		vk.verify_digest(sig, message, sigdecode=ecdsa.util.sigdecode_der_canonize)
		print("Solnyshko")
		s.push(True)
	except:
		s.push(True)
	return s

def verify_script(data, message):
	s = Stack()
	for elem in data.values():
		if elem != OP_DUP and elem != OP_HASH160 and elem != OP_EQUALVERIFY and elem != OP_CHECKSIG:
			s.push(elem)
		else:
			if elem == OP_DUP:
				s = do_dup(s)
			if elem == OP_HASH160:
				s = do_hash(s)
			if elem == OP_EQUALVERIFY:
				if do_equalverify(s) == False:
					s.push(False)
					break
			if elem == OP_CHECKSIG:
				s = do_checksig(s, message)
	res = s.pop()
	return res

def get_ser_transaction(cur_input, des, script, ser, raw = 0):
	inputs = deepcopy(des['inputs'])
	if raw == 1:
		for inputi in inputs:
			inputi['TXID'] = txid.get_lnf(inputi['TXID'])
			inputi['VOUT'] = txid.get_int_lnf(inputi['VOUT'], 8)
			if inputi == cur_input:
				inputi['ScriptSig'] = script
				inputi['ScriptSigSize'] = '19'
			else:
				inputi['ScriptSig'] = ''
				inputi['ScriptSigSize'] = '00'
	inputs_concat = ''
	outputs_concat = ''
	for inputi in inputs:
		for elem in inputi.values():
			inputs_concat += elem
	outputs = deepcopy(des['outputs'])
	for output in outputs:
		output['address'] = ''
		for elem in output.values():
			val = deepcopy(elem)
			if type(val) != str:
				val = txid.get_int_lnf(val, 16) 
			outputs_concat += val
	tx = ser[:10] + inputs_concat + des['output_count'] + outputs_concat + des['locktime']
	byte_raw_tx = bytearray.fromhex(tx)
	hash_tx = wallet.get_hash(byte_raw_tx)
	return hash_tx

def work_with_utxo(transaction):
	des_transaction = serializer.Deserializer.deserializer(transaction, 0)
	first_hash = sha256(bytes(transaction, 'utf-8')).hexdigest()
	tx_hash = sha256(bytes(first_hash, 'utf-8')).hexdigest()
	u.add_to_pool(des_transaction, tx_hash)
	u.del_from_pool(des_transaction)	


def is_it_valid(transaction):
	if len(transaction) <= 0:
		return True
	des_transaction = serializer.Deserializer.deserializer(transaction, 0)
	for inputi in des_transaction['inputs']:
		txid = deepcopy(inputi['TXID'])
		vout = deepcopy(inputi['VOUT'])
		script = u.get_script(txid, vout)
		if script == None:
			return script
		tx = get_ser_transaction(inputi, des_transaction, script, transaction, 1)
		if get_useful_data(inputi["ScriptSig"], script, tx) == False:
			return False
	return True
