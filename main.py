from flask import Flask, request, jsonify 
from flask_cors import CORS
import threading
from bot import order_on_amazon
import stripe
import os

app = Flask(__name__)
CORS(app, origins=["https://jigglesngiggles.github.io"])

if os.environ.get("TEST_MODE"):
    stripe.api_key = os.environ.get("STRIPE_SECRET_TEST_KEY")  # set this in Render
else: 
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # set this in Render

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            shipping_address_collection={
                "allowed_countries": ["US"]
            },
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Mosquito Zapper",
                    },
                    "unit_amount": 5999,  # $59.99 in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://yourdomain.com/success",  # update if needed
            cancel_url="https://yourdomain.com/cancel",
        )
        return jsonify(id=session.id)
    except Exception as e:
        return jsonify(error=str(e)), 400
    
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    if os.environ.get("TEST_MODE"):
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_TEST_SECRET")  # set this in Render
    else:
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")  # set this in Render

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        return "Webhook signature verification failed.", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_details = session.get("customer_details", {})
        shipping = session.get("shipping", {})
        address = shipping.get("address", {})

        threading.Thread(target=order_on_amazon, args=(
            customer_details.get("name", ""),
            address.get("line1", ""),
            address.get("city", ""),
            address.get("state", ""),
            address.get("postal_code", ""),
            False  # not test mode
        )).start()

    return "", 200

#if __name__ == "__main__":
#    app.run(debug=True)