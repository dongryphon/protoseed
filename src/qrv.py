#!/usr/bin/env python3
from pathlib import Path

import base58
import os
import qrcode
import qrcode.image.svg

#import lxml.etree as ET
import xml.etree.ElementTree as ET

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
        module_drawer='circle'  # SvgPathCircleDrawer()
    )
    # img.save(outputFile)

    def stripNs(el):
        tag = el.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        c = ET.Element(tag)
        for k, v in el.attrib.items():
            if k != 'xmlns':
                c.set(k, v)
        for sub in el:
            c2 = stripNs(sub)
            c.append(c2)
        return c

    s = img.to_string()
    svg1 = stripNs(ET.fromstring(s))
    pathEl = None

    for el in svg1:
        if el.tag.endswith('path'):
            pathEl = el
            break

    if pathEl is not None:
        svg1.remove(pathEl)
        ident = pathEl.attrib['id']

        defsEl = ET.Element('defs')
        svg1.append(defsEl)
        defsEl.append(pathEl)

        tree = ET.ElementTree(svg1)
        tree.write(outputFile, encoding='utf-8', xml_declaration=True)


def main():
    try:
        generate_qr_svg(generateSeed(), DIR / 'qr.svg')

        print("QR code generated successfully!")

    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return False


if __name__ == '__main__':
    main()  # *sys.argv[1:]
