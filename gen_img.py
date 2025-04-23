import os
from PIL import Image, ImageDraw, ImageFont
import string

# Directory to save images
output_dir = 'resources\images'
os.makedirs(output_dir, exist_ok=True)

# Image settings
width, height = 720, 1280
background_color = (255, 255, 255)  # white
text_color = (0, 0, 0)              # black
font_size = 500

# Load a system font (you can adjust the path to a .ttf file if needed)
try:
    font = ImageFont.truetype("arial.ttf", font_size)
except IOError:
    font = ImageFont.load_default()

# Generate 20 images labeled A–T
letters = string.ascii_uppercase[:20]  # 'A' through 'T'

for letter in letters:
    # Create blank image
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate text size and position for centering
    # Option A: use the classic (but now-deprecated) textsize method
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width  - text_w)  / 2
    y = (height - text_h) / 2
    
    # Draw the letter
    draw.text((x, y), letter, fill=text_color, font=font)
    
    # Save to disk
    filepath = os.path.join(output_dir, f"{letter}.png")
    img.save(filepath)

print(f"Generated {len(letters)} images in '{output_dir}'")
