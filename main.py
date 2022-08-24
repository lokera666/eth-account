'''

Authenticate + serve a bitcoin wallet for every replit user.
Note: still very much in beta.

'''

from flask import Flask, render_template, request, send_file, redirect
from utils import generate, export_btc_wallet_as_json, get_address_from_wif, send_btc, get_btc_balance_api, get_btc_price
from replit import db
import os

app = Flask('app')

@app.route('/')
def index():
    '''Default endpoint.'''
    user_id = request.headers['X-Replit-User-Id']
    user_name=request.headers['X-Replit-User-Name']
    # if not authenticated
    if '' in [user_id, user_name]:
      return render_template('wallet.html')
    # if authenticated
    else:
      # if the user has a replwallet
      if f'{user_id}-BTCWIF' in db.keys():
        wif = db[f'{user_id}-BTCWIF']
        return render_template(
            'wallet.html',
            user_id=user_id,
            user_name=user_name,
            address=get_address_from_wif(wif),
            btc_balance=get_btc_balance_api(wif), 
            btc_price=get_btc_price()
        )
      # if the user has not created a replwallet before
      else:
        wif = generate()
        db[f'{user_id}-BTCWIF'] = wif
        return render_template(
            'wallet.html',
            user_id=user_id,
            user_name=user_name,
            address=get_address_from_wif(wif),
            btc_balance=get_btc_balance_api(wif), 
            btc_price=get_btc_price()
        )


@app.route('/setupBTCSend', methods=['GET'])
def send_bitcoin():
    user_id = request.headers['X-Replit-User-Id']
    user_name=request.headers['X-Replit-User-Name']
    # if not authenticated
    if '' in [user_id, user_name]:
      return redirect('https://wallet.sorenrood.repl.co')
    # if authenticated
    else:
      return render_template('setup_send.html', user_id=user_id, user_name=user_name)


@app.route('/sendBTC', methods=['POST'])
def sendBTC():
  user_id = request.headers['X-Replit-User-Id']
  user_name=request.headers['X-Replit-User-Name']
  # if not authenticated
  if '' in [user_id, user_name]:
    return redirect('https://wallet.sorenrood.repl.co')
  # if authenticated
  else:
    address = request.form.get("address")
    amount = request.form.get("BTC")
    wif = db[f'{user_id}-BTCWIF']
    balance = get_btc_balance_api(wif)
    # if the user does not have enough BTC
    if float(amount) > float(balance):
      return render_template('not_enough_btc.html', balance=balance, amount=amount)
    # if the user has enough BTC
    try:
      tx = send_btc(wif, amount, address)
      tx_link = 'https://www.blockchain.com/btc/tx/' + tx
      value_usd = 'dollar_value_calculate_later'
      return render_template(
        'sent.html',
        user_id=user_id,
        user_name=user_name,
        address=address,
        amount=amount, 
        value_usd=value_usd,
        tx_link=tx_link
      )
    except Exception as e:
      return render_template('error_tx.html', error=e)
  

@app.route('/downloadBTCWallet')
def download_bitcoin_wallet():
    user_id = request.headers['X-Replit-User-Id']
    user_name=request.headers['X-Replit-User-Name']
    # if not authenticated
    if '' in [user_id, user_name]:
      return redirect('https://wallet.sorenrood.repl.co')
    # if authenticated
    else:
      wif = db[f'{user_id}-BTCWIF']
      filename = export_btc_wallet_as_json(wif, user_name)
      file = send_file(filename, as_attachment=True)
      os.remove(filename)
      return file


app.run(host='0.0.0.0', port=8080)