from flask import Flask, request, jsonify
import threading
from bot import order_on_amazon
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Load this from env vars!
app = Flask(__name__)

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Mosquito Zapper",
                        "images": ["https://m.media-amazon.com/images/I/61GksKdNtkL._AC_SL1500_.jpg"],
                    },
                    "unit_amount": 5999,  # $59.99 in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://your-site.com?status=success",
            cancel_url="https://your-site.com?status=cancel",
            shipping_address_collection={
                "allowed_countries": ["US"],
            }
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400
    
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")  # set in Render

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        shipping = session.get("shipping", {})
        address = shipping.get("address", {})
        name = shipping.get("name", "")

        # Trigger bot
        threading.Thread(target=order_on_amazon, args=(name, address.get("line1", ""), address.get("city", ""), address.get("postal_code", ""), True)).start()
        #true for test, false for prod

    return jsonify(success=True)

#if __name__ == "__main__":
#    app.run(debug=True)