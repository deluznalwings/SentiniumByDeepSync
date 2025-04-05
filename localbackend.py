from fastapi import FastAPI
import pickle
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 🔹 Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# 🔹 Firebase setup
cred = credentials.Certificate(r"D:\Sentinium\localservicekey.json")  # 🔸 Use your actual service account key filename
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔹 FastAPI setup
app = FastAPI()

@app.get("/")
def root():
    return {"message": "✅ FastAPI is connected to Firebase and running"}

@app.post("/process_next")
def process_next_comment():
    try:
        # 🔸 Step 1: Get the next unprocessed document
        docs = db.collection("requests").where("processed", "==", False).limit(1).stream()
        doc = next(docs, None)

        if not doc:
            return {"message": "🎉 All comments processed"}

        doc_ref = db.collection("requests").document(doc.id)
        data = doc.to_dict()

        comment = data.get("comment")
        userid = data.get("userid")  # ← Your database uses 'userid' not 'user_id'

        if not comment:
            return {"error": "⚠️ Comment field is missing"}

        print(f"\n📩 Processing comment from user {userid}: {comment}")

        # 🔸 Step 2: Model prediction
        predictions = model.predict(comment)

        print("📤 Predictions:")
        for item in predictions:
            print(f"  → Aspect: {item['span']} | Polarity: {item['polarity']}")

        # 🔸 Step 3: Update the document
        doc_ref.update({
            "response": predictions,      # Update response field
            "processed": True             # Mark as processed
        })

        return {
            "message": "✅ Processed successfully",
            "userid": userid,
            "comment": comment,
            "response": predictions
        }

    except Exception as e:
        return {"error": str(e)}
