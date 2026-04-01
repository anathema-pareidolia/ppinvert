#!/usr/bin/env python
# ppinvert.py
import argparse
import imagequant
from PIL import Image, ImageOps


def main():
  parser = argparse.ArgumentParser(
                    prog='ppinvert',
                    description='ppinvert takes a color input image, quantizes it to produce a palette of colors it uses as well as a grayscale version of the image, inverts the grayscale, and reapplies the palette. I made it to preserve the sepia-like stain of black and white film developed with a staining developer like Pyrocat-HD when scanning a film negative instead of printing one.',
                    epilog='Written March 16, 2026 by Anathema.')
  parser.add_argument('infile', help='A path to the image to invert. It must be in an RGB or RGBA format, of a filetype supported by Pillow (see https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html).')
  parser.add_argument('outfile', nargs='?', default=None, help='A file path indicating where to write the inverted image. By default, ppinvert will write to the same path as infile, like so: /path/to/infile.tif -> /path/to/infile_ppinv.tif')
  parser.add_argument('-q', '--quantizer', choices=['mediancut', 'maxcoverage', 'fastoctree', 'libimagequant', 'lossless'], default='libimagequant', help='Which quantizing algorithm to use. Pillow has four built-in options to choose from. mediancut and maxcoverage do not support RGBA images; transparency will be lost if an RGBA image is provided with one of those quantization methods. All of them will compress the color space of an image to at most 256 colors. lossless is a planned experimental method for preserving all color data in the original image.')
  parser.add_argument('-d', '--debug', action='store_true', help='automatically save interstitial images generated in the process.')
  args = parser.parse_args()
  infile = args.infile
  if not args.outfile:
    outfile = "_ppinv.".join(infile.rsplit('.', 1))
  else:
    outfile = args.outfile
  match args.quantizer:
    case 'lossless':
      print("The lossless quantizer is not yet implemented, but I appreciate your enthusiasm and optimism.")
      exit()
    case 'mediancut':
      quantizer = Image.Quantize.MEDIANCUT
    case 'maxcoverage':
      quantizer = Image.Quantize.MAXCOVERAGE
    case 'fastoctree':
      quantizer = Image.Quantize.FASTOCTREE
    case 'libimagequant':
      quantizer = 'imagequant'
    case _:
      raise ValueError("unspecified quantizer, somehow")
  debug = args.debug
  neg = Image.open(infile)
  neg_gray = ImageOps.grayscale(neg)
  if debug:
    neg_gray.save("_gray.".join(outfile.rsplit('.',1)))
  pos = ImageOps.invert(neg_gray)
  if debug:
    pos.save("_inv.".join(outfile.rsplit('.',1)))
  palette = None
  if quantizer == 'imagequant':
    palette = imagequant.quantize_pil_image(
      neg,
      dithering_level=0.0,
      max_colors=256,
      min_quality=0,
      max_quality=100)
  else:
    palette = neg.quantize(256, quantizer)
  if debug:
    palette.save("_quant.".join(outfile.rsplit('.',1)))
  remap = pos.remap_palette(range(256,-1,-1), palette.getpalette(rawmode="RGB"))
  remap.save(outfile)

if __name__ == "__main__":
  main()
