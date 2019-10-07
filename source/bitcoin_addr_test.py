import unittest
import wallet

ADDR = 'mh3pDbJ9dukSoisepwpGzCLFTKVPYU91k7'

class TestBitcoinAddress(unittest.TestCase):
	def test_address_from_priv(self):
		private_key = 'e6b3a66524b26dd81d0841cc77d31a39aaefc157d6486487885b1cc7cd017a52'
		my_addr = wallet.get_bitcoin_address(private_key)
		self.assertEqual(my_addr, ADDR)

	def test_address_from_pub(self):
		public_key = '0461cc57bcf945b80884f0d69d0aa721ca829ca232d9c58a1ae40bdb3d5f36850feea3602031c63abcd693ee38c5d488cc480ce6f21ac9d2f40dd7405190104374'
		self.assertEqual(wallet.get_bitcoin_address_from_public_key(public_key), ADDR)

	def test_address_from_comp(self):
		compressed_key = '0361cc57bcf945b80884f0d69d0aa721ca829ca232d9c58a1ae40bdb3d5f36850f'
		self.assertEqual(wallet.get_address_from_compressed_key(compressed_key), ADDR)

if __name__ == "__main__":
    unittest.main()
