'''

Util functions for replit wallet.
Note: still very much in beta.

'''

from bit import Key, wif_to_key
import requests
import json


def generate():
    '''Generate a Key and turn it into a WIF.'''
    return Key().to_wif()


def get_btc_balance_api(wif: str):
  '''Get the balance of an address.'''
  try:
    endpoint = 'https://www.bitgo.com/api/v1/address/'
    address = wif_to_key(wif).address
    sats = json.loads(requests.get(endpoint + address).content.decode('utf-8'))['balance']
    btc = int(sats) / 100000000
    return btc
  except:
    return 'Error getting wallet balance.'


def get_btc_price():
  '''Get the current price of BTC.'''
  try:
    endpoint = "https://api.blockchain.com/v3/exchange/tickers/BTC-USD"
    resp = json.loads(requests.get(endpoint).content.decode('utf-8'))
    return resp['last_trade_price']
  except:
    return 'Error getting BTC price.'


def send_btc(wif: str, amount: float, address: str):
  '''A function to send BTC.'''
  key = wif_to_key(wif)
  outputs = [(address, amount, 'btc')]
  print(f"Sending {amount} to {address}!")
  resp = key.send(outputs)
  print(f"Resp: {resp}")
  return resp


def get_address_from_wif(wif: str):
  '''A function to get the public address from a users WIF.'''
  return wif_to_key(wif).address


def export_btc_wallet_as_json(wif: str, user_name):
    '''
    This function will export the private key, 
    public key, and address for a user's wallet as a json file.
    Will return the filename it created. Delete the file after from local storage.
    '''
    key = wif_to_key(wif)
    public_key = key.public_key.hex()
    priv_key = key._pk.to_hex()
    address = key.address
    wallet = {
      "username": user_name,
      "coin": "BTC",
      "address": address,
      "public_key": public_key,
      "private_key": priv_key
    }
    filename = f'{user_name}-BTCWallet.json'
    with open(filename, 'w') as o:
      json.dump(wallet, o)
    return filename