from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
from bs4 import BeautifulSoup
import demoji
import emot
from textblob import TextBlob

# Load the sentiment analysis model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)
CORS(app)

# Preprocessing functions
def to_lowercase(text):
    return text.lower()

def remove_html_tags(text):
    return BeautifulSoup(text, "html.parser").get_text()

def remove_urls(text):
    return re.sub(r"http\S+|www\S+|bit.ly\S+", "", text)
#def handle_emoji_and_emoticons(text):
    #emot_obj = emot.core.emot()
    #result = emot_obj.emoticons(text)
    #for emoticon, meaning in zip(result['value'], result['mean']):
        #text = text.replace(emoticon, meaning)
    #emojis = demoji.findall(text)
    #for emoji, desc in emojis.items():
        #text = text.replace(emoji, f", {desc.split(':')[0]} ")
    #return text

def remove_excessive_punctuation(text):
    return re.sub(r'([!?.,]){2,}', r'\1', text)

def correct_spelling(text):
    return str(TextBlob(text).correct())

def preprocess_text(text):
    text = to_lowercase(text)
    text = remove_html_tags(text)
    text = remove_urls(text)
    #text = handle_emoji_and_emoticons(text)
    text = remove_excessive_punctuation(text)
    text = correct_spelling(text)
    return text

@app.route('/')
def home():
    return "✅ Sentiment Analysis API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'error': 'Expected a list of dictionaries'}), 400

        results = []
        for entry in data:
            comment = entry.get("comment")
            user_id = entry.get("user_id")
            if not comment or not user_id:
                return jsonify({'error': 'Each dictionary must contain "comment" and "user_id" keys'}), 400

            processed_comment = preprocess_text(comment)
            predictions = model.predict([processed_comment])

            results.append({
                'original_comment': comment,
                'processed_comment': processed_comment,
                'aspects': predictions,
                'user_id': user_id
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
