from fastapi import FastAPI
from pydantic import BaseModel
from firebase_admin import credentials, initialize_app, db
import firebase_admin
import pickle
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
cred = credentials.Certificate("serviceacckey.json")  # ✅ Make sure this JSON file is in the same folder
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://sentinium-3306c-default-rtdb.firebaseio.com"
})
app = FastAPI()
class CommentData(BaseModel):
    username: str
    comment: str
@app.get("/")
def read_root():
    return {"message": "✅ FastAPI ABSA Model is Running!"}
@app.post("/predict")
def predict(data: CommentData):
    comment = data.comment
    username= data.username
    predictions = model.predict(comment)
    print("\n🧠 Received Comment:", comment)
    print("✅ Model Output:")
    for item in predictions:
        print(f"  → Aspect: {item['span']}, Polarity: {item['polarity']}")
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
