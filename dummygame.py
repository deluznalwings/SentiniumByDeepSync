import gradio as gr
from PIL import Image, ImageDraw
import random
import time

# Load your image
imageurl = r"C:\Users\hp\Downloads\9a090454ab8f5b24b7adf37d66be44d5.jpg"
try:
    dummyimage = Image.open(imageurl)
except:
    # Create a dummy image if file not found
    dummyimage = Image.new('RGB', (800, 600), color='lightgray')
    draw = ImageDraw.Draw(dummyimage)
    draw.text((300, 280), "Sample Image", fill='black')

# Object annotations (x, y, width, height)
annotations = {
    "Watch": (244, 574, 69, 54),
    "Glasses": (342, 435, 152, 51),
    "Gun": (194, 221, 117, 227)
}

def start_game():
    """Initialize and start the game"""
    objects_to_find = random.sample(list(annotations.keys()), 3)
    current_index = 0
    found_objects = []
    
    # Show first object to find
    current_obj = objects_to_find[current_index]
    label = f"**Find and click on: {current_obj}**"
    feedback = f"Game started! Looking for object 1/3: {current_obj}"
    
    game_state = {
        'objects_to_find': objects_to_find,
        'current_index': current_index,
        'found_objects': found_objects,
        'waiting_for_click': True,
        'game_active': True
    }
    
    return (
        label,                           # label
        dummyimage,                     # img  
        feedback,                       # feedback
        gr.update(visible=False),       # start_button (hide)
        gr.update(visible=True),        # next_button (show)
        game_state                      # game_state
    )

def check_click(evt: gr.SelectData, game_state):
    """Handle image clicks"""
    if not game_state or not game_state.get('game_active', False):
        return (
            "Please start the game first!",
            dummyimage,
            "Click 'Start Game' to begin",
            gr.update(visible=True),     # start_button
            gr.update(visible=False),    # next_button  
            game_state
        )
    
    if not game_state.get('waiting_for_click', False):
        return (
            game_state.get('current_label', ''),
            dummyimage,
            "Please wait or click 'Next Object'...",
            gr.update(visible=False),
            gr.update(visible=True),
            game_state
        )
    
    # Get click coordinates
    cx, cy = evt.index
    
    # Get current object to find
    objects_to_find = game_state['objects_to_find']
    current_index = game_state['current_index']
    curr_obj = objects_to_find[current_index]
    x, y, w, h = annotations[curr_obj]
    
    # Check if click is within the object bounds
    if x <= cx <= x + w and y <= cy <= y + h:
        # Correct click!
        game_state['found_objects'].append(curr_obj)
        game_state['waiting_for_click'] = False
        
        # Create highlighted image
        highlighted_img = dummyimage.copy()
        draw = ImageDraw.Draw(highlighted_img)
        draw.rectangle([x, y, x + w, y + h], outline="green", width=6)
        
        # Move to next object
        game_state['current_index'] += 1
        
        # Check if game is complete
        if game_state['current_index'] >= len(objects_to_find):
            game_state['game_active'] = False
            return (
                "🎉 **CONGRATULATIONS! You found all objects!** 🎉",
                highlighted_img,
                f"Game Won! Found all objects: {', '.join(game_state['found_objects'])}",
                gr.update(visible=True, value="Start New Game"),   # start_button
                gr.update(visible=False),                          # next_button
                game_state
            )
        
        # Prepare next object info
        next_obj = objects_to_find[game_state['current_index']]
        game_state['next_object'] = next_obj
        
        feedback = f"✅ Correct! Found {curr_obj}. Click 'Next Object' to continue ({game_state['current_index']}/3 complete)"
        
        return (
            f"✅ **Found: {curr_obj}!** Click 'Next Object' to continue...",
            highlighted_img,
            feedback,
            gr.update(visible=False),    # start_button
            gr.update(visible=True),     # next_button
            game_state
        )
    
    else:
        # Wrong click
        return (
            f"❌ **Wrong location!** Try clicking on the **{curr_obj}**",
            dummyimage,
            f"Try again! Looking for: {curr_obj}",
            gr.update(visible=False),    # start_button
            gr.update(visible=True),     # next_button
            game_state
        )

def show_next_object(game_state):
    """Show the next object to find"""
    if not game_state or not game_state.get('game_active', False):
        return start_game()
    
    current_index = game_state['current_index']
    objects_to_find = game_state['objects_to_find']
    
    if current_index >= len(objects_to_find):
        return (
            "Game completed!",
            dummyimage,
            "All objects found!",
            gr.update(visible=True, value="Start New Game"),
            gr.update(visible=False),
            game_state
        )
    
    current_obj = objects_to_find[current_index]
    game_state['waiting_for_click'] = True
    
    label = f"**Find and click on: {current_obj}**"
    feedback = f"Looking for object {current_index + 1}/3: {current_obj}"
    
    return (
        label,
        dummyimage,  # Reset to original image
        feedback,
        gr.update(visible=False),    # start_button
        gr.update(visible=True),     # next_button
        game_state
    )

# Create Gradio interface
with gr.Blocks(title="Object Finding Game", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 Object Finding Game")
    gr.Markdown("**Instructions:** Click on the objects as they are requested. Find all 3 objects to win!")
    
    # Game state storage
    game_state = gr.State({})
    
    with gr.Row():
        with gr.Column(scale=3):
            label = gr.Markdown("**Click 'Start Game' to begin!**", elem_id="game-label")
            img = gr.Image(
                value=dummyimage, 
                interactive=True, 
                height=600,
                elem_id="game-image"
            )
        
        with gr.Column(scale=1):
            feedback = gr.Textbox(
                label='Game Status', 
                interactive=False, 
                value="Ready to start!",
                lines=3
            )
            
            start_button = gr.Button(
                'Start Game', 
                variant="primary", 
                size="lg"
            )
            
            next_button = gr.Button(
                'Next Object', 
                variant="secondary", 
                visible=False,
                size="lg"
            )
            
            gr.Markdown("---")
            gr.Markdown("### 📋 How to Play:")
            gr.Markdown("1. Click **Start Game**")
            gr.Markdown("2. Click on the highlighted object")
            gr.Markdown("3. Click **Next Object** to continue")
            gr.Markdown("4. Find all 3 objects to win!")
            
            gr.Markdown("### 🎯 Objects to Find:")
            gr.Markdown("• Watch ⌚")
            gr.Markdown("• Glasses 👓") 
            gr.Markdown("• Gun 🔫")
    
    # Event handlers
    start_button.click(
        fn=start_game,
        inputs=[],
        outputs=[label, img, feedback, start_button, next_button, game_state]
    )
    
    img.select(
        fn=check_click,
        inputs=[game_state],
        outputs=[label, img, feedback, start_button, next_button, game_state]
    )
    
    next_button.click(
        fn=show_next_object,
        inputs=[game_state],
        outputs=[label, img, feedback, start_button, next_button, game_state]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1")
