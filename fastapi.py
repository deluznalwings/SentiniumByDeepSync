from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import firebase_admin
from firebase_admin import credentials, db

# 🔹 Load your trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# 🔹 Initialize Firebase
cred = credentials.Certificate("serviceacckey.json")  # ✅ Your Firebase Admin SDK key
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://sentinium-3306c-default-rtdb.firebaseio.com"
})

# 🔹 Initialize FastAPI app
app = FastAPI()

# 🔹 Define request format
class CommentData(BaseModel):
    username: str
    comment: str

# 🔹 Home route to check server status
@app.get("/")
def read_root():
    return {"message": "✅ FastAPI ABSA Model is Running!"}

# 🔹 Prediction route
@app.post("/predict")
def predict(data: CommentData):
    try:
        comment = data.comment
        username = data.username

        # 🔮 Run your model's prediction
        predictions = model.predict(comment)

        print("\n🧠 Received Comment:", comment)
        print("✅ Model Output:")
        for item in predictions:
            print(f"  → Aspect: {item['span']}, Polarity: {item['polarity']}")

        # 🔁 Save predictions to Firebase
        ref = db.reference(f"/predictions/{username}")
        ref.set({
            "comment": comment,
            "aspects": predictions
        })

        return {
            "username": username,
            "comment": comment,
            "aspects": predictions
        }
    except Exception as e:
        return {"error": str(e)}

