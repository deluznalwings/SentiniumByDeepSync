from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, initialize_app, firestore
import pickle

# Load your sentiment analysis model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate(r"D:\Sentinium\localservicekey.json")
firebase_app = initialize_app(cred)
db = firestore.client()

@app.get("/analyze-comment/{doc_id}")
async def analyze_comment(doc_id: str):
    """Get comment from document, analyze it, write results back"""
    try:
        # Get the document
        doc_ref = db.collection("requests").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract comment
        doc_data = doc.to_dict()
        comment = doc_data.get("comment")
        
        if not comment:
            raise HTTPException(status_code=400, detail="No comment found in document")
        
        # Process with model
        predictions = model.predict(comment)
        
        # Write predictions back to document
        doc_ref.update({
            "sentiment_results": predictions
        })
        
        return {
            "comment": comment,
            "results": predictions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
