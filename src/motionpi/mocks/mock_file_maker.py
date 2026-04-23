import random
from PIL import Image, ImageDraw


IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
BACKGROUND_COLOUR = "black"
STICKMAN_COLOUR = "blue"


def create_mock_jpg(path):

    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOUR)
    draw = ImageDraw.Draw(image)

    # keep stickman fully inside frame
    x = random.randint(60, IMAGE_WIDTH - 60)
    y = random.randint(80, IMAGE_HEIGHT - 80)

    # head
    head_radius = 20
    draw.ellipse(
        [(x - head_radius, y - head_radius), (x + head_radius, y + head_radius)],
        outline=STICKMAN_COLOUR,
        width=3,
    )

    # body
    draw.line([(x, y + 20), (x, y + 100)], fill=STICKMAN_COLOUR, width=3)

    # arms
    draw.line([(x - 30, y + 45), (x + 30, y + 45)], fill=STICKMAN_COLOUR, width=3)

    # legs
    draw.line([(x, y + 100), (x - 30, y + 140)], fill=STICKMAN_COLOUR, width=3)
    draw.line([(x, y + 100), (x + 30, y + 140)], fill=STICKMAN_COLOUR, width=3)

    image.save(path)

    return path


if __name__ == "__main__":
    create_mock_jpg("stickman_test.jpg")
