#!/usr/bin/env python3
from pathlib import Path

import base58
import os
import qrcode
import qrcode.image.svg

import segno

from qrcode.image.styles.moduledrawers.svg import SvgPathCircleDrawer
from qrcode.image.svg import SvgPathImage

DIR = Path(__file__).joinpath('../..').resolve()


# qr = segno.make('Vampire Blues')
# qr.save(DIR / 'vampire-blues.svg', border=5)


def generateSeed():
    data = os.urandom(96)
    encoded = base58.b58encode(data).decode('ascii')

    return f'protoseed:/p/{encoded}'


def generate_qr_svg(data, outputFile, scale=10):
    qr = qrcode.QRCode(
        version=11,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        # image_factory=SvgCircleImage,
        image_factory=SvgPathImage,
        box_size=scale,
        border=1
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        module_drawer=SvgPathCircleDrawer()
    )
    img.save(outputFile)


def main():
    try:
        generate_qr_svg(generateSeed(), DIR / 'qr.svg')

        print("QR code generated successfully!")

    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return False


if __name__ == '__main__':
    main()  # *sys.argv[1:]
