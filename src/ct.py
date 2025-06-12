from PIL import Image, ImageDraw, ImageFont
import math


def draw_circular_text(text, radius, font_path, font_size, output_path):
    # Create a blank white image
    size = radius * 2 + 100  # Add padding
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Load font
    font = ImageFont.truetype(font_path, font_size)

    # Calculate center of the image
    center_x = size // 2
    center_y = size // 2

    # Draw circle outline for reference
    draw.ellipse([50, 50, size-50, size-50], outline='black')

    # Calculate angle for each character
    text_length = len(text)
    angle_per_char = 360 / text_length

    for i, char in enumerate(text):
        # Calculate angle in radians
        angle = math.radians(angle_per_char * i - 90)  # Start at top (-90 degrees)

        # Calculate position for the character
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        # Create a temporary image for the character
        char_image = Image.new('RGBA', (font_size * 2, font_size * 2), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)

        # Draw character
        char_draw.text((font_size // 2, font_size // 2), char, font=font, fill='black')

        # Rotate the character
        char_image = char_image.rotate(angle_per_char * i, resample=Image.BICUBIC)

        # Paste the character onto the main image
        image.paste(char_image, (int(x - font_size // 2), int(y - font_size // 2)), char_image)

    # Save the image
    image.save(output_path)

def main():
    # Example usage
    text = "HELLO WORLD AROUND CIRCLE"
    radius = 100
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_size = 20
    output_path = "circular_text.png"

    draw_circular_text(text, radius, font_path, font_size, output_path)

if __name__ == '__main__':
    main()
