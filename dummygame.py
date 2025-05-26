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

def start_new_game():
    """Start a completely new game"""
    objects_list = random.sample(list(annotations.keys()), 3)
    
    initial_state = {
        'objects_to_find': objects_list,
        'current_index': 0,
        'found_objects': [],
        'game_active': True,
        'waiting_for_click': True,
        'show_highlighted': False
    }
    
    current_obj = objects_list[0]
    label_text = f"🎯 **FIND: {current_obj}** (Object 1 of 3)"
    feedback_text = f"Game Started! Click on the {current_obj} in the image."
    
    return (
        label_text,
        dummyimage,
        feedback_text,
        initial_state
    )

def create_success_highlight(base_image, found_objects_list):
    """Create green highlight for all correctly found objects"""
    highlighted_img = base_image.copy()
    draw = ImageDraw.Draw(highlighted_img)
    
    # Highlight all found objects
    for obj_name in found_objects_list:
        obj_x, obj_y, obj_w, obj_h = annotations[obj_name]
        
        # Green rectangle around each found object
        draw.rectangle([obj_x, obj_y, obj_x + obj_w, obj_y + obj_h], 
                      outline="lime", width=8)
        
        # Inner green border for emphasis
        draw.rectangle([obj_x + 2, obj_y + 2, obj_x + obj_w - 2, obj_y + obj_h - 2], 
                      outline="green", width=4)
    
    return highlighted_img

import time

def create_single_highlight(base_image, object_name):
    """Highlight only the recently found object"""
    highlighted_img = base_image.copy()
    draw = ImageDraw.Draw(highlighted_img)
    
    obj_x, obj_y, obj_w, obj_h = annotations[object_name]
    draw.rectangle([obj_x, obj_y, obj_x + obj_w, obj_y + obj_h], 
                   outline="lime", width=6)
    draw.rectangle([obj_x + 2, obj_y + 2, obj_x + obj_w - 2, obj_y + obj_h - 2], 
                   outline="green", width=3)
    return highlighted_img

def handle_image_click(evt: gr.SelectData, current_state):
    if not current_state or not current_state.get('game_active', False):
        return (
            "❌ No active game. Click 'Start Game' first!",
            dummyimage,
            "Please start a new game.",
            {'game_active': False}
        )
    
    if not current_state.get('waiting_for_click', False):
        return (
            current_state.get('last_label', 'Wait...'),
            dummyimage,
            "Please wait, processing...",
            current_state
        )
    
    click_x, click_y = evt.index
    objects_to_find = current_state['objects_to_find']
    current_index = current_state['current_index']
    current_obj = objects_to_find[current_index]
    
    obj_x, obj_y, obj_w, obj_h = annotations[current_obj]
    
    if obj_x <= click_x <= obj_x + obj_w and obj_y <= click_y <= obj_y + obj_h:
        # Correct!
        current_state['found_objects'].append(current_obj)
        current_state['current_index'] += 1
        current_state['waiting_for_click'] = False  # Pause for effect
        
        # Highlight only the latest object
        temp_highlight_img = create_single_highlight(dummyimage, current_obj)
        
        # Save transition info
        current_state['last_highlight'] = temp_highlight_img
        
        # Game complete?
        if current_state['current_index'] >= len(objects_to_find):
            current_state['game_active'] = False
            current_state['waiting_for_click'] = False
            return (
                "🎉 **GAME WON! ALL OBJECTS FOUND!** 🎉",
                temp_highlight_img,
                f"🏆 Victory! Found all: {', '.join(current_state['found_objects'])}",
                current_state
            )
        
        # Show highlight for a moment, then return to original image
        next_obj = objects_to_find[current_state['current_index']]
        object_num = current_state['current_index'] + 1
        label_text = f"🎯 **FIND: {next_obj}** (Object {object_num} of 3)"
        feedback_text = f"✅ Found {current_obj}! Now find the {next_obj}."

        # Update state
        current_state['waiting_for_click'] = True
        current_state['last_label'] = label_text
        
        # Return highlight first
        return (
            label_text,
            temp_highlight_img,
            feedback_text,
            current_state
        )
    
    else:
        label_text = f"🎯 **FIND: {current_obj}** (Object {current_index+1} of 3)"
        feedback_text = f"❌ MISS! Try clicking directly on the {current_obj}."
        return (
            label_text,
            dummyimage,
            feedback_text,
            current_state
        )


# Create the Gradio interface
with gr.Blocks(title="Object Finding Game") as demo:
    
    gr.Markdown("# 🎯 Object Finding Game")
    gr.Markdown("**Goal:** Find and click on 3 different objects in the image!")
    
    # State variable
    game_state = gr.State({})
    
    with gr.Row():
        with gr.Column(scale=2):
            # Main game label
            game_label = gr.Markdown("**Click 'Start Game' to begin!**", elem_id="main-label")
            
            # The clickable image
            game_image = gr.Image(
                value=dummyimage,
                interactive=True,
                height=500,
                show_label=False
            )
            
        with gr.Column(scale=1):
            # Feedback area
            feedback_box = gr.Textbox(
                label="Status",
                value="Ready to play!",
                interactive=False,
                lines=4
            )
            
            # Start game button
            start_btn = gr.Button("🎮 Start Game", variant="primary", size="lg")
            
            gr.Markdown("---")
            gr.Markdown("### Objects to Find:")
            gr.Markdown("• ⌚ **Watch**")
            gr.Markdown("• 👓 **Glasses**") 
            gr.Markdown("• 🔫 **Gun**")
            
            gr.Markdown("### Instructions:")
            gr.Markdown("1. Click **Start Game**")
            gr.Markdown("2. Look for the requested object")
            gr.Markdown("3. Click directly on it")
            gr.Markdown("4. Continue until all 3 are found!")
    
    # Event bindings
    start_btn.click(
        fn=start_new_game,
        inputs=[],
        outputs=[game_label, game_image, feedback_box, game_state]
    )
    
    game_image.select(
        fn=handle_image_click,
        inputs=[game_state],
        outputs=[game_label, game_image, feedback_box, game_state]
    )

if __name__ == "__main__":
    demo.launch()
