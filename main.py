from math import sqrt, floor
from typing import Dict, Set
from mcipc.rcon.je import Client
from PIL import Image

# coordinates for top-left corner of image
x, y, z = 0, 4, 0


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def distance(self, other):
        return sqrt(
            (self.r - other.r) ** 2 + \
            (self.g - other.g) ** 2 + \
            (self.b - other.b) ** 2
        )


class Block:
    def __init__(self, line):
        parts = line.strip().split(' ')
        self.name = parts[0]
        r, g, b = (int(x) for x in parts[1:])
        self.color = Color(r, g, b)


def read_blocks(filename):
    """Read the blocks from blocks.txt, returning them as a set of Block instances."""
    blocks = set()
    with open(filename) as file:
        for line in file:
            blocks.add(Block(line))
    return blocks


def read_image(filename):
    """Read the image, scaling it down if needed. Return pixels, width and height."""
    with Image.open(filename) as img:
        width, height = img.size
        if width > 256 or height > 256:
            print(f'Image too big ({width}x{height}), scaling down.')
            biggest = max(width, height)
            factor = 256 / biggest
            width = floor(width * factor)
            height = floor(height * factor)
            img = img.resize((width, height))
            print(f'Resized image to {width}x{height}.')
        pixels = img.load()
    return pixels, width, height


def nearest_block(nearest_so_far: Dict[Color, Block], blocks: Set[Block], color):
    """
    Return the block corresponding to the color in `nearest_so_far` if one exists, or find the closest block in
    `blocks`, add it to the dict, and then return it if it was not already there.
    """
    if color in nearest_so_far:
        return nearest_so_far.get(color)
    else:
        block = min(
            blocks,
            key=lambda b: color.distance(b.color)
        )
        nearest_so_far[color] = block
        return block


def main():
    blocks = read_blocks('blocks.txt')
    pixels, width, height = read_image('image.jpg')

    nearest_so_far = {}  # cache found blocks to prevent future lookups - works best with flat-color images
    with Client('127.0.0.1', 25575, passwd='cuzco') as client:
        print(f'Starting to print {width} columns')
        for i in range(width):
            print(f'Printing col {i}...')
            for j in range(height):
                r, g, b = pixels[i, j]
                color = Color(r, g, b)
                block = nearest_block(nearest_so_far, blocks, color).name
                client.setblock((x+i, y, z+j), f'minecraft:{block}')


if __name__ == '__main__':
    main()
