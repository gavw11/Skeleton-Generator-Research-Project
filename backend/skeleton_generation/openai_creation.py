from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
from PIL import Image

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=API_KEY)

def generate_image(prompt):
    response = client.images.generate(
        model='dall-e-3',
        prompt = (
            f"{prompt}, clearly visible and centered in the frame, "
            "with high contrast against the background, well-lit, and "
            "no occlusions or background clutter. Ensure the entire subject is within view and that subjects don't overlap with each other."
        ),
        size='1024x1024',
        quality='standard',
        n=1
    )

    image_url = response.data[0].url

    return image_url

def save_generation(prompt, save_path):

    image_url = generate_image(prompt)

    # Download the image from the URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    
    save_path = os.path.join(save_path)
    
    # Save the image
    image.save(save_path)
