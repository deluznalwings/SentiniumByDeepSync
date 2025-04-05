from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Load your model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# 🔐 Firebase Setup
cred = credentials.Certificate('serviceacckey.json')  # Replace with your file name if different
firebase_admin.initialize_app(cred)
db = firestore.client()  # This gives you access to Firestore DB

# Root route
@app.route('/')
def home():
    return "✅ Sentiment Analysis API is running!"

# Prediction + Firebase storing route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        comment = data.get("comment")

        if not comment:
            return jsonify({'error': 'Missing "comment" field in request'}), 400

        # Run ABSA model
        predictions = model.predict(comment) # Limiting to top 2 predictions
        for item in predictions:
            print(f"  → Aspect: {item['span']}, Polarity: {item['polarity']}")
        result = {
            'comment': comment,
            'aspects': predictions
        }
        db.collection('comments').add(result)  # 'comments' is your collection name

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
