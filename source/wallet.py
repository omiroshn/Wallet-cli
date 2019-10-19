import hashlib
import binascii
import base58
import codecs
import ecdsa
import os
import utxo_set as utxo
import transaction
import serializer
from hashlib import sha256
import struct
from ecdsa.curves import SECP256k1
import bech32

CURVE_ORDER = SECP256k1.order

def convert_to_WIF(privkey):
	privkey_v = 'ef' + privkey + '01'
	first_sha256 = hashlib.sha256(binascii.unhexlify(privkey_v)).hexdigest()
	second_sha256 = hashlib.sha256(binascii.unhexlify(first_sha256)).hexdigest()
	final_key = privkey_v + second_sha256[:8]
	WIF = base58.b58encode(binascii.unhexlify(final_key))
	return WIF

def get_swaddress(private_key):
	public_key = get_public_key(private_key)
	compressed_key = get_compressed_key(public_key)
	swaddr = get_bech32(compressed_key)
	return swaddr

def get_bech32(compressed_publkey):
	hrp = 'tb'
	witver = 0
	sha256 = hashlib.sha256(bytes.fromhex(compressed_publkey))
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256.digest())
	witprog = ripemd160.digest()
	bech32_addr = bech32.encode(hrp, witver, witprog)
	return bech32_addr

def WIF_to_key(WIF):
	base_normal = binascii.hexlify(base58.b58decode(WIF))
	private_key = binascii.hexlify(codecs.decode(base_normal[2:-8], 'hex')).decode() 
	if private_key[64:] == '01':
		private_key = private_key[:-2]
	return private_key

def normalize_secret_bytes(privkey_bytes: bytes) -> bytes:
    scalar = string_to_number(privkey_bytes) % CURVE_ORDER
    if scalar == 0:
        raise Exception('invalid EC private key scalar: zero')
    privkey_32bytes = number_to_string(scalar, CURVE_ORDER)
    return privkey_32bytes

def get_private_key():
	private_key = os.urandom(32)
	private_key = binascii.hexlify(private_key)
	return binascii.hexlify(codecs.decode(private_key, 'hex')).decode()


def get_public_key(priv_key):
	priv_key = codecs.decode(priv_key, 'hex')
	sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	publ_key = '04' + binascii.hexlify(vk.to_string()).decode()
	return publ_key

def get_compressed_key(pub_key):
	key = pub_key[2:66]
	if (int(key[len(key) - 1], 16) % 2 != 0):
		compressed_key = '03' + key
	else:
		compressed_key = '02' + key
	return compressed_key


def get_checksum(encrypting_pub_key):
	encrypting_pub_key = codecs.decode(encrypting_pub_key, 'hex')
	sha256_nbpk = hashlib.sha256(encrypting_pub_key)
	sha256_nbpk_digest = sha256_nbpk.digest()
	sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
	sha256_2_nbpk_digest = sha256_2_nbpk.digest()
	sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
	checksum = sha256_2_hex[:8]
	checksum = binascii.hexlify(codecs.decode(checksum, 'hex')).decode()
	return checksum

def encrypting_pubkey(public_key):
	public_key_bytes = codecs.decode(public_key, 'hex')
	sha256_bpk = hashlib.sha256(public_key_bytes)
	sha256_bpk_digest = sha256_bpk.digest()
	ripemd160_bpk = hashlib.new('ripemd160')
	ripemd160_bpk.update(sha256_bpk_digest)
	ripemd160_bpk_digest = ripemd160_bpk.digest()
	ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
	encr = "6F" + binascii.hexlify(codecs.decode(ripemd160_bpk_hex, 'hex')).decode()
	return encr


def base58_my(address_hex):
	alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	b58_string = ''
	leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
	address_int = int(address_hex, 16)
	while address_int > 0:
		digit = address_int % 58
		digit_char = alphabet[digit]
		b58_string = digit_char + b58_string
		address_int //= 58
	ones = leading_zeros // 2
	for one in range(ones):
		b58_string = '1' + b58_string
	return b58_string

def get_address_from_compressed_key(compressed_key):
	encrypting_pub_key = encrypting_pubkey(compressed_key)
	checksum = get_checksum(encrypting_pub_key)
	bitcoin_address = base58_my(encrypting_pub_key + checksum)
	return bitcoin_address

def get_bitcoin_address_from_public_key(uncompressed_public_key):
	compressed_key = get_compressed_key(uncompressed_public_key)
	return get_address_from_compressed_key(compressed_key)

def get_bitcoin_address(private_key):
	uncompressed_public_key = get_public_key(private_key)
	bitcoin_address = get_bitcoin_address_from_public_key(uncompressed_public_key)
	return bitcoin_address

def sign(priv_key, message):
    sk = ecdsa.SigningKey.from_string(binascii.unhexlify(priv_key), curve=ecdsa.SECP256k1)
    pub_key = sk.get_verifying_key();
    sig = sk.sign_digest(message, sigencode=ecdsa.util.sigencode_der_canonize)
    return {'sign' : sig, 'pub_key' : pub_key}


def create_raw_input(inputs_info, count):
	raw_inputs = []
	i = 0
	for info in inputs_info:
		if i == count: 
			raw_inputs.append(transaction.Input(info['tx_hash_big_endian'], info['tx_output_n'], 1, info['script']))
		else:
			raw_inputs.append(transaction.Input(info['tx_hash_big_endian'], info['tx_output_n'], 1, ''))
		i += 1
	return raw_inputs

def create_inputs(inputs_info, sig_key):
	inputs = []
	i = 0
	for info in inputs_info:
		inputs.append(transaction.Input(info['tx_hash_big_endian'], info['tx_output_n'], sig_key[i]))
		i += 1
	return inputs

def create_outputs(recipient_addr, my_addr, amount, balance, segwit):
	outputs = []
	if amount < balance:
		outputs.append(transaction.Output(amount, recipient_addr, segwit))
		outputs.append(transaction.Output(balance - amount, my_addr, segwit))
	else:
		outputs.append(transaction.Output(amount, recipient_addr, segwit))
	return outputs

def create_transaction(inputik, output):
	trans = transaction.Transaction(1, inputik, output, 0)
	trans = trans.get_full_transaction()
	return trans

def get_hash(raw_transaction):
	hash_tx = hashlib.sha256(hashlib.sha256(raw_transaction).digest()).digest()
	return hash_tx

def get_raw_transaction(inputs_info, addr, my_addr, amount, balance, privkey, outputs):
	sig_key = []
	for i in range(len(inputs_info)):
		raws_inputiki = create_raw_input(inputs_info, i)
		raw_transaction = create_transaction(raws_inputiki, outputs)
		raw_transaction_ser = serializer.Serializer.serializer(raw_transaction)
		raw_transaction_ser = raw_transaction_ser + '01000000'
		byte_raw_tx = bytearray.fromhex(raw_transaction_ser)
		hash_tx = get_hash(byte_raw_tx)
		sig_key.append(sign(privkey, hash_tx))
	return sig_key, outputs, raws_inputiki 

def send(addr, amount, privkey, where):
	my_addr = get_bitcoin_address(privkey)
	utxo_set = utxo.get_utxo_set(where, my_addr)
	fee = int((amount * 0.1) / 100)
	balance = utxo.check_balance(utxo_set)
	if balance < amount:
		 print("\033[1;31;40mHey, hey, hey! Not so fast, you have not so much money!")
		 print("\033[1;33;40mYour balance: %d\n" % balance)
		 return
	inputs_info, balance = utxo.get_inputs_info(utxo_set, (int(amount) + fee))
	outputs = create_outputs(addr, my_addr, amount, balance, 0)
	sig_key, outputs, raw_inputs = get_raw_transaction(inputs_info, addr, my_addr, amount, balance, privkey, outputs)
	inputiki = create_inputs(inputs_info, sig_key)
	tx = create_transaction(inputiki, outputs)
	tx_sr = serializer.Serializer.serializer(tx)
	return tx_sr

