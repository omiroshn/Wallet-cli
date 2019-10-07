import config
import binascii
import unittest
import wallet

PUBLIC_KEY = '0461cc57bcf945b80884f0d69d0aa721ca829ca232d9c58a1ae40bdb3d5f36850feea3602031c63abcd693ee38c5d488cc480ce6f21ac9d2f40dd7405190104374'
COMPRESSED = '0361cc57bcf945b80884f0d69d0aa721ca829ca232d9c58a1ae40bdb3d5f36850f'
WIF = 'cVK9z4gBcunZU9LRVCaK6Q4xAqMnW7Gx6rGSEMFfiDZ4F7i6TDX1'
PRIVKEY = 'e6b3a66524b26dd81d0841cc77d31a39aaefc157d6486487885b1cc7cd017a52'

class TestBitcoinKeys(unittest.TestCase):

	def test_public_key(self):
		self.assertEqual(wallet.get_public_key(PRIVKEY), PUBLIC_KEY)

	def test_compressed_key(self):
		self.assertEqual(wallet.get_compressed_key(PUBLIC_KEY), COMPRESSED)

	def test_wif(self):
		self.assertEqual(wallet.convert_to_WIF(PRIVKEY), WIF)

	def test_privkey_wif(self):
		self.assertEqual(wallet.WIF_to_key(WIF), PRIVKEY)

if __name__ == "__main__":
    unittest.main()
