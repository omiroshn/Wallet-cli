import wallet
import transaction
import codecs
import binascii
import base58
import serializer
import ecdsa


def availabilyty_of_address(recipient):
	address_decode = binascii.hexlify(base58.b58decode(recipient))
	encrypted_key = address_decode[:-8]
	valid_checksum = wallet.get_checksum(encrypted_key)
	checksum = binascii.hexlify(codecs.decode(address_decode[42:], 'hex')).decode()
	if valid_checksum != checksum:
		return False
	return True


def verify_sender(pub_key, sender_addr):
	addr_of_key = wallet.get_bitcoin_address_from_public_key(pub_key)
	return addr_of_key == sender_addr


def validity_of_signature(sig, pub_key, sender, recipient, amount):
	message = transaction.Transaction(sender, recipient, amount)
	message = message.transaction_hash_calculate()
	sig = codecs.decode(sig, 'hex')
	vk = ecdsa.VerifyingKey.from_string(codecs.decode(pub_key[2:], 'hex'), curve=ecdsa.SECP256k1)
	try:
		vk.verify(sig, bytes(message, 'utf-8'), sigdecode=ecdsa.util.sigdecode_der)
		return True
	except:
		return False


def validation(transaction):
	inform = serializer.Deserializer.deserializer(transaction)
	amount = inform['amount']
	sender_addr = inform['sender']
	print(sender_addr)
	recipient_addr = inform['recipient']
	public_key = inform['public_key']
	signature = inform['signature']
	if availabilyty_of_address(sender_addr) == False:
		print("Something get wrong! You have some problem with your address!!")
		return False
	if availabilyty_of_address(recipient_addr) == False:
		print("Something get wrong! You have some problem with recipient address!!")
		return False
	if verify_sender(public_key, sender_addr) == False:
		print("Something get wrong! You have some problem with your public key or address")
		return False
	if validity_of_signature(signature, public_key, sender_addr, recipient_addr, amount) == False:
		print("Something get wrong! You have some problem with the signature!!")
		return False
	return True 
