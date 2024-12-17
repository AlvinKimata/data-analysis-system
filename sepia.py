import gradio as gr

def load_image(image_path):
    """
    Load and return an image from the specified file path.
    
    Args:
        image_path (str): Path to the PNG image file
    
    Returns:
        The loaded image
    """
    return image_path

# Create the Gradio interface
demo = gr.Interface(
    fn=load_image,
    inputs=gr.Textbox(label=""),
    outputs=gr.Image(label="Loaded Image"),
    title="PNG Image Loader",
    description="Enter the full path to a PNG image to display it"
)

# Launch the interface
if __name__ == "__main__":
    demo.launch()