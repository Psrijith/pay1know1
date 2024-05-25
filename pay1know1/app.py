from flask import Flask, redirect, request, jsonify, render_template
import stripe
import firebase_admin
from firebase_admin import credentials, db ,firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"./pay1know1-firebase-adminsdk-ygtp2-e3d66ef7d2.json")  
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pay1know1-default-rtdb.asia-southeast1.firebasedatabase.app/'   
})

# Create a reference to your Firebase Realtime Database
db_ref = db.reference('/')

stripe.api_key = 'sk_test_51PKDhjSGlv3owL3wZuw2GzKQABpylNYWGTBLMuXBSzk5cpVgFDIPzpyrPlY1PFO2CKSg97c0v1XTPLlQcNxtj71E00dzGYSM3b'

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

def get_successful_payments_count():
    try:
        count = db_ref.child('successful_payments').get()
        if count is None:
            count = 0
        return count
    except Exception as e:
        app.logger.error("Error retrieving count of successful payments from Firebase: %s", str(e))
        return None

def increment_successful_payments_count():
    try:
        count = get_successful_payments_count()
        if count is not None:
            db_ref.child('successful_payments').set(count + 1)
        else:
            app.logger.error("Unable to increment count of successful payments. Count retrieval failed.")
    except Exception as e:
        app.logger.error("Error incrementing count of successful payments in Firebase: %s", str(e))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-session', methods=['POST'])
def create_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            billing_address_collection='required',
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'pay1know1'
                        },
                        'unit_amount': 1
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='http://localhost:4242/payment/success',
            cancel_url='http://localhost:4242/payment/failure',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/payment/success')
def payment_success():
    try:
        increment_successful_payments_count()
        count = get_successful_payments_count()
        if count is not None:
            return render_template('success.html', count=count)
        else:
            return render_template('success.html', count='Count retrieval failed')
    except Exception as e:
        app.logger.error("Error processing successful payment: %s", str(e))
        return render_template('success.html', count='Error processing payment')

@app.route('/payment/failure')
def payment_failure():
    return render_template('index.html', error="Payment failed. Please try again.")

if __name__ == '__main__':
    app.run(port=4242)