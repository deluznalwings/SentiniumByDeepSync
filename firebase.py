from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, initialize_app, firestore
import pickle
import uvicorn

# Load sentiment analysis model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = FastAPI(title="Sentiment Analysis API")

# Initialize Firebase - adjust the path to your credentials file
cred = credentials.Certificate(r"D:\Sentinium\localservicekey.json")
firebase_app = initialize_app(cred)
db = firestore.client()

@app.get("/")
def read_root():
    return {"status": "Sentiment Analysis API is running"}

@app.get("/analyze/{doc_id}")
async def analyze_comment(doc_id: str):
    """Analyze a comment from Firebase and write results back"""
    try:
        # Get document reference
        doc_ref = db.collection("requests").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        # Get comment from document
        doc_data = doc.to_dict()
        comment = doc_data.get("comment")
        
        if not comment:
            raise HTTPException(status_code=400, detail="No comment found in document")
        
        # Process with model - this will return format like [{'span': 'food', 'polarity': 'negative'}]
        sentiment_results = model.predict(comment)
        
        # Write results back to Firebase
        doc_ref.update({
            "sentiment_results": sentiment_results
        })
        
        return {
            "document_id": doc_id,
            "comment": comment,
            "sentiment_results": sentiment_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/process-all")
async def process_all_unprocessed():
    """Process all unprocessed comments in the database"""
    try:
        # Query for unprocessed documents
        query = db.collection("requests").where("processed", "==", False).stream()
        
        results = []
        for doc in query:
            doc_id = doc.id
            doc_data = doc.to_dict()
            comment = doc_data.get("comment")
            
            if comment:
                # Get sentiment analysis results
                sentiment_results = model.predict(comment)
                
                # Update document with results
                db.collection("requests").document(doc_id).update({
                    "sentiment_results": sentiment_results
                })
                
                results.append({
                    "document_id": doc_id,
                    "comment": comment,
                    "sentiment_results": sentiment_results
                })
        
        return {"processed_count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing requests: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
