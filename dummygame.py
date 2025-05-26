
import gradio as gr
from PIL import Image, ImageDraw
import random
import time
import threading

# Load your image
imageurl = r"C:\Users\hp\Downloads\9a090454ab8f5b24b7adf37d66be44d5.jpg"
dummyimage = Image.open(imageurl)

# Object annotations (x, y, width, height)
annotations = {
    "Watch": (244, 574, 69, 54),
    "Glasses": (342, 435, 152, 51),
    "Gun": (194, 221, 117, 227)
}

# Game state
class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.current_index = 0
        self.found_indexes = set()
        self.waiting_for_click = False
        self.objects_to_find = random.sample(list(annotations.keys()), 3)
        self.game_started = False

state = GameState()

def show_next_label():
    """Show the next object to find"""
    if state.current_index >= len(state.objects_to_find):
        return "🎉 You found all objects! You won!", dummyimage, "Game completed!", gr.update(visible=True, value="Start New Game")
    
    current_obj = state.objects_to_find[state.current_index]
    label = f"Click on the **{current_obj.replace('_', ' ')}**"
    state.waiting_for_click = True
    
    return label, dummyimage, f"Looking for: {current_obj}", gr.update(visible=False)

def start_game():
    """Initialize and start the game"""
    state.reset()
    state.game_started = True
    return show_next_label()

def delayed_next_object():
    """Show next object after delay"""
    time.sleep(2.5)  # 2.5 second delay
    return show_next_label()

def check_click(evt: gr.SelectData):
    """Handle image clicks"""
    if not state.game_started:
        return "Please start the game first!", dummyimage, "Click 'Start Game' to begin", gr.update(visible=True, value="Start Game")
    
    if not state.waiting_for_click:
        return "Wait for the next object label...", dummyimage, "Please wait...", gr.update(visible=False)
    
    # Get click coordinates
    cx, cy = evt.index
    
    # Get current object to find
    curr_obj = state.objects_to_find[state.current_index]
    x, y, w, h = annotations[curr_obj]
    
    # Check if click is within the object bounds
    if x <= cx <= x + w and y <= cy <= y + h:
        # Correct click!
        state.found_indexes.add(state.current_index)
        state.waiting_for_click = False
        
        # Create highlighted image
        highlighted_img = dummyimage.copy()
        draw = ImageDraw.Draw(highlighted_img)
        draw.rectangle([x, y, x + w, y + h], outline="green", width=6)
        
        # Move to next object
        state.current_index += 1
        
        # Check if game is complete
        if state.current_index >= len(state.objects_to_find):
            state.game_started = False
            return "🎉 Congratulations! You found all objects!", highlighted_img, "Game Won! 🏆", gr.update(visible=True, value="Start New Game")
        
        # Show success message and prepare for next object
        feedback = f"✅ Correct! Found {curr_obj}. Next object in 3 seconds..."
        
        # Use threading to handle the delay without blocking
        def show_next_after_delay():
            time.sleep(3)
            return show_next_label()
        
        # Start timer for next object
        timer_thread = threading.Thread(target=lambda: None)  # Placeholder
        timer_thread.start()
        
        return feedback, highlighted_img, f"Found: {curr_obj} ✅", gr.update(visible=False)
    
    else:
        # Wrong click
        return f"❌ Wrong location! Try clicking on the {curr_obj}.", dummyimage, f"Try again: {curr_obj}", gr.update(visible=False)

def continue_game():
    """Continue to next object (called by timer or button)"""
    if state.current_index < len(state.objects_to_find):
        return show_next_label()
    else:
        return "Game completed!", dummyimage, "All done!", gr.update(visible=True, value="Start New Game")

# Create Gradio interface
with gr.Blocks(title="Object Finding Game") as demo:
    gr.Markdown("# 🎯 Object Finding Game")
    gr.Markdown("Click on the objects as they are requested. You have 3 objects to find!")
    
    with gr.Row():
        with gr.Column():
            label = gr.Markdown("Click 'Start Game' to begin!")
            img = gr.Image(value=dummyimage, interactive=True, height=600)
        
        with gr.Column(scale=0.3):
            feedback = gr.Textbox(label='Status', interactive=False, value="Ready to start!")
            start_button = gr.Button('Start Game', variant="primary")
            continue_button = gr.Button('Next Object', visible=False)
            
            gr.Markdown("### Instructions:")
            gr.Markdown("1. Click 'Start Game'")
            gr.Markdown("2. Click on the requested object")
            gr.Markdown("3. Wait for the next object")
            gr.Markdown("4. Repeat until all found!")
    
    # Event handlers
    start_button.click(
        fn=start_game,
        inputs=None,
        outputs=[label, img, feedback, start_button]
    )
    
    img.select(
        fn=check_click,
        outputs=[feedback, img, label, start_button]
    )
    
    continue_button.click(
        fn=continue_game,
        outputs=[label, img, feedback, start_button]
    )

if __name__ == "__main__":
    demo.launch()
