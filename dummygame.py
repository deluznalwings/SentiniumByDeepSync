import gradio as gr
from PIL import Image,ImageDraw
import random
imageurl=r"C:\Users\hp\Downloads\9a090454ab8f5b24b7adf37d66be44d5.jpg"
dummyimage=Image.open(imageurl)
annotations={"Watch":(244,574,69,54),
             "Glasses":(342,435,152,51),
             "Gun":(194,221,117,227)
             }
objectstofind=random.sample(list(annotations.keys()), 3)
state={
    'currentindex':0,
    "foundindexes":set(),
    "highlightimg": dummyimage.copy(),
    "waitingforclick":False
}
def shownextlabel():
  if state['currentindex']>=len(objectstofind):
    return "You win the game",None, gr.update(visible=False)
  label = f"Click on the **{objectstofind[state['currentindex']].replace('_', ' ')}**"
  state["waitingforclick"] = True
  state["highlightimg"] = dummyimage.copy()
  return label, state["highlightimg"], gr.update(visible=True)
def startgame():
  state['currentindex']=0
  state['foundindexes']=set()
  state["highlightimg"] = dummyimage.copy()
  state["waitingforclick"] = False
  return shownextlabel()
def checkclick(evt:gr.SelectData):
  if not state["waitingforclick"]:
    return "Wait for the next object label...", state["highlightimg"], gr.update(visible=True)
  cx, cy = evt.index
  curr_obj = objectstofind[state["currentindex"]]
  x, y, w, h = annotations[curr_obj]
  if x <= cx <= x + w and y <= cy <= y + h:
    # Correct click!
    state["foundindexes"].add(state["currentindex"])
    state["waitingforclick"] = False

    # Draw green rectangle on highlight_img
    img = state["highlightimg"].copy()
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + w, y + h], outline="green", width=4)
    state["highlightimg"] = img

    # Move to next object after short delay (simulate label fade)
    state["currentindex"] += 1
    if state["currentindex"] >= len(objectstofind):
      return "🎉 You found all objects! You won!", img, gr.update(visible=False)

    return f"✅ Correct! Next object coming up...", img, gr.update(visible=True)
  else:
    # Wrong click - try again
    return "❌ Wrong! Try again.", state["highlightimg"], gr.update(visible=True)
with gr.Blocks() as demo:
  label=gr.Markdown("")
  img=gr.Image(value=dummyimage, interactive=True)
  feedback=gr.Textbox(label='Feedback', interactive=False)
  next_button=gr.Button('Start Game')
  next_button.click(fn=startgame,inputs=None, outputs=[label,img,feedback])
  img.select(fn=checkclick, outputs=[feedback,img,label])
demo.launch()
