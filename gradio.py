import gradio as gr
import pickle
with open("model.pkl", "rb") as f:
    model = pickle.load(f)
def analyze_comment(comment):
    predictions = model.predict(comment)
    result = ""
    for p in predictions:
        result += f"Aspect: {p['span']}, Sentiment: {p['polarity']}\n"
    return result.strip()
iface = gr.Interface(
    fn=analyze_comment,
    inputs=gr.Textbox(lines=4, placeholder="Enter your Text: "),
    outputs="text",
    title="ABSA Model",
    description="Aspect-Based Sentiment Analysis"
)
iface.launch()
