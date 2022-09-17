import hmac
import hashlib
import json
import codecs
import time
import requests


def hook(qrlpay_secret, invoice, order_id):
    key = codecs.decode(qrlpay_secret, "hex")

    # Calculate a secret that is required to send back to the
    # woocommerce gateway, proving we did not modify id nor amount.
    secret_seed = str(int(100 * float(invoice["dollar_value"]))).encode("utf-8")
    print("Secret seed: {}".format(secret_seed))

    secret = hmac.new(key, secret_seed, hashlib.sha256).hexdigest()

    # The main signature  which proves we have paid, and very recently!
    paid_time = int(time.time())
    params = {"wc-api": "wc_qrlpay_gateway", "time": str(paid_time), "id": order_id}
    message = (str(paid_time) + "." + json.dumps(params, separators=(",", ":"))).encode(
        "utf-8"
    )
    print("Message from hook: " + str(message))

    # Calculate the hash
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Signature": hash,
        "X-Secret": secret,
        "tx_id": invoice["payment_id"],
    }

    # Send the webhook response, confirming the payment with woocommerce.
    response = requests.get(invoice["webhook"], params=params, headers=headers)

    return response
