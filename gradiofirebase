import gradio as gr
import pickle
import time
import firebase_admin
from firebase_admin import credentials, db
FIREBASE_URL = "https://sentinium-c0c28-default-rtdb.firebaseio.com/"
cred = credentials.Certificate(r"D:\Sentinium\privatekey.json")
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_URL})
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

def write_comment(comment_text):
    """Push comment to Firebase under /comments"""
    ref = db.reference("comments")
    new_ref = ref.push({
        "text": comment_text,
        "timestamp": int(time.time())
    })
    return new_ref.key

def update_prediction(comment_id, predictions):
    """Update the predictions for a comment"""
    db.reference(f"comments/{comment_id}/predictions").set(predictions)

def format_predictions(predictions):
    """Format list of dicts to display nicely in Gradio"""
    result = ""
    for p in predictions:
        result += f"✅ **Aspect:** {p['span']}  —  **Sentiment:** {p['polarity']}\n\n"
    return result.strip()

def analyze_and_store(comment):
    comment_id = write_comment(comment)
    predictions = model.predict(comment)  # Must return a list of dicts
    update_prediction(comment_id, predictions)
    return format_predictions(predictions)


with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Markdown("""
    # 🧠 ABSA with Firebase
    Predict aspect-based sentiments in Hinglish comments and store results in Firebase.
    """, elem_id="title")

    with gr.Row():
        input_box = gr.Textbox(label="Enter your comment", lines=4, placeholder="Type your comment here...")
        output_box = gr.Text(label="📊 Model Predictions")

    submit_btn = gr.Button("Run ABSA")

    submit_btn.click(fn=analyze_and_store, inputs=input_box, outputs=output_box)

demo.launch(share=True)
