from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "✅Sentiment Analysis API is running!"
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        comment = data.get("comment")
        if not comment:
            return jsonify({'error': 'Missing "comment" field in request'}), 400
        predictions = model.predict(comment) 
        print("\n🧠 Received Comment:", comment)
        print("✅ Model Output:")
        for item in predictions:
            print(f"  → Aspect: {item['span']}, Polarity: {item['polarity']}")
        return jsonify({
            'comment': comment,
            'aspects': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5000)
  
