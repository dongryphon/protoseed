#!/usr/bin/env python3
from pathlib import Path

import base58
import math
import os
import qrcode
import sys

from PIL import Image, ImageDraw

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer


DIR = Path(__file__).joinpath('../..').resolve()
ETC = DIR / 'etc'
CWD = Path(os.getcwd())


def generateSeed():
    data = os.urandom(96)
    encoded = base58.b58encode(data).decode('ascii')

    return f'protoseed:{encoded}'


def generateQR(uri):
    # Configure QR code
    qr = qrcode.QRCode(
        version=11,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each module in pixels
        border=1  # Quiet zone (4 modules)
    )

    # Add URI to QR code
    qr.add_data(uri)
    qr.make(fit=True)

    #img = qr.make_image(image_factory=StyledPilImage, module_drawer=CircleModuleDrawer())
    #img.save("circular_qr.png")

    qrImage = qr.make_image(fill_color="black", back_color="white", image_factory=StyledPilImage, module_drawer=CircleModuleDrawer()).convert('RGBA')
    qrSize = qrImage.size[0]  # QR code width (e.g., 610 pixels for Version 11)

    qrImage.save(DIR / "qr.png")

    left = 0
    top = qrSize // 3
    right = qrSize
    bottom = 2 * qrSize//3

    cropImage = qrImage.crop((left, top, right, bottom))
    rotatedCropImage = cropImage.copy()
    rotatedCropImage = rotatedCropImage.rotate(90, expand=True)

    # Load and resize logo
    logo_path = str(ETC / 'logo.png')
    logo = Image.open(logo_path).convert('RGBA')

    logo_size = logo.size[0]

    # Calculate position to center logo
    logo_pos = ((qrSize - logo_size) // 2, (qrSize - logo_size) // 2)

    # Overlay logo on QR code
    qrImage.paste(logo, logo_pos, logo)  # Use logo's alpha channel for transparency

    # Save the final image
    qrImage.save(DIR / "qr_with_logo.png")

    frameSize = 8
    radius = math.ceil(math.sqrt(2) * qrSize / 2) + frameSize
    roundSize = radius * 2
    dx = radius - math.ceil(qrSize / 2)
    # print(f'squareSize = {qrSize} => roundSize = {roundSize} => radius = {radius} => dx = {dx}')

    img2 = Image.new('RGBA', (roundSize, roundSize), (0, 0, 0, 0))

    # fill top
    img2.paste(cropImage, (dx, 0) )
    # fill bottom
    img2.paste(cropImage, (dx, img2.size[1] - cropImage.size[1]) )
    # fill left
    img2.paste(rotatedCropImage, (0, dx) )
    # fill right
    img2.paste(rotatedCropImage, (img2.size[0] - rotatedCropImage.size[0], dx) )

    dr = ImageDraw.Draw(img2)
    dr.ellipse([(-dx,-dx), (img2.size[0] + dx, img2.size[1] + dx)], outline=(0,0,0,0), width=dx)
    dr.ellipse([(0,0), img2.size], outline='black', width=frameSize)

    pos = (roundSize - qrSize) // 2, (roundSize - qrSize) // 2
    img2.paste(qrImage, pos)

    img2.save(CWD / 'round.png')


def main(*args):
    uri = generateSeed()
    print(f'uri[{len(uri)}]: {uri}')
    generateQR(uri)


if __name__ == '__main__':
    main(*sys.argv[1:])
