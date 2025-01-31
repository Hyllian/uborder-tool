import os
import string
import sys
import argparse
from PIL import Image

def verify(name, val1, val2, default):
    class Validity(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            val = values
            if values < val1 or values > val2:
                print("WARNING:",name, "must be between", val1,"and",val2,". Setting to default=", default)
                val = default
            setattr(namespace, self.dest, val)
    return Validity

def parseCommandArgs():
    parser = argparse.ArgumentParser(description="Estimates coordinates from the inner rectangle based on alpha transparent image.")
    parser.add_argument("image_file", help="input file (32-bit png)")
    parser.add_argument("-o", "--output", dest="output", required=False, help="output file (file to output uborder params)")
    parser.add_argument("-s", "--step", type=int, metavar='INT[1,100]', help="search step size (bigger is faster, though less precise).", action=verify("step", 1, 100, 5))
    parser.add_argument("-t", "--threshold", type=int, metavar='INT[1,255]', help="threshold below which transparent pixel is detected.", action=verify("threshold", 1, 255, 100))
    parser.add_argument("-p", "--preview", action="store_true", help="print results and show an image with detected points in green.")
    return parser.parse_args()

def main():
    args = parseCommandArgs()

    step        = args.step
    threshold   = args.threshold

    pixels  = Image.open(args.image_file).convert('RGBA')

    w, h = pixels.size

    left, up = pixels.size
    right = 0
    down = 0

    game_orient = "HORIZONTAL"

    for i in range(0, w, step):
        for j in range(0, h, step):
            r,g,b,a = pixels.getpixel((i,j))
            if a < threshold:
                left  = min( left, i)
                up    = min(   up, j)
                right = max(right, i)
                down  = max( down, j)


    for i in range(max(0, left-step), left+step, 1):
        for j in range(0, h, step):
            r,g,b,a = pixels.getpixel((i,j))
            if a < threshold and left != i:
                left  = min( left, i)

    for i in range(right-step, min(w, right+step), 1):
        for j in range(0, h, step):
            r,g,b,a = pixels.getpixel((i,j))
            if a < threshold:
                right  = max(right, i)

    for i in range(0, w, step):
        for j in range(max(0, up-step), up+step, 1):
            r,g,b,a = pixels.getpixel((i,j))
            if a < threshold:
                up  = min(up, j)

    for i in range(0, w, step):
        for j in range(down-step, min(h, down+step), 1):
            r,g,b,a = pixels.getpixel((i,j))
            if a < threshold:
                down  = max(down, j)

    width  = right - left
    height = down - up

    left_norm   = left/pixels.width
    up_norm     = up/pixels.height
    height_norm = height/pixels.height
    width_norm  = width/pixels.width

    if width < height:
        game_orient = "VERTICAL"


    aspect_ratio_n = height/width
    aspect_ratio   = 8*height/width

    h1080 = height_norm * 1080
    w1080 = width_norm * 1920
    x1080 = left_norm * 1920
    y1080 = up_norm * 1080

    center_x = (width  + 2.0*left - w) / (2*width)
    center_y = (height + 2.0*up   - h) / (2*height)

    zoom = (100*min(1.0, aspect_ratio_n)*width_norm)

    if w < h and game_orient == "HORIZONTAL":
        h1080 = height_norm * 1920
        w1080 = width_norm * 1080
        x1080 = left_norm * 1080
        y1080 = up_norm * 1920

    h4k = h1080 * 2
    w4k = w1080 * 2
    x4k = x1080 * 2
    y4k = y1080 * 2

    h1440p = (h4k / 3) * 2
    w1440p = (w4k / 3) * 2
    x1440p = (x4k / 3) * 2
    y1440p = (y4k / 3) * 2


    if args.preview:
        print("\nImage Resolution = ", pixels.size)
        print("Game Orientation (estimated) = ", game_orient)
        print("\nOptions:\n\tSearch Step = ", step)
        print("\tTransparency Threshold = ", threshold)
        print("\nResults:\n\tViewport Height = (Norm.: \"%2.6f\"), (1080p: %4d), (1440p: %4d), (4k: %4d)" % (height_norm, h1080, h1440p, h4k))
        print("\tViewport Width  = (Norm.: \"%2.6f\"), (1080p: %4d), (1440p: %4d), (4k: %4d)" % (width_norm, w1080, w1440p, w4k))
        print("\tViewport X      = (Norm.: \"%2.6f\"), (1080p: %4d), (1440p: %4d), (4k: %4d)" % (left_norm, x1080, x1440p, x4k))
        print("\tViewport Y      = (Norm.: \"%2.6f\"), (1080p: %4d), (1440p: %4d), (4k: %4d)" % (up_norm, y1080, y1440p, y4k))
        print("\nUborder parameters:\n\tAspect Ratio = (Norm.: \"1.0\", \"%2.6f\"), (\"8.0\", \"%2.6f\")" % (aspect_ratio_n, aspect_ratio))
        print("\tZOOM     = \"%2.6f\")" % zoom)
        print("\tcenter_x = \"%2.6f\"" % (100*center_x))
        print("\tcenter_y = \"%2.6f\"" % (100*center_y))
        r = 10

        for i in range(-r, +r):
            for j in range(-r, r):
                pixels.putpixel( (i +  left, j +   up), (r, 255, b, a) )
                pixels.putpixel( (i + right, j +   up), (r, 255, b, a) )
                pixels.putpixel( (i +  left, j + down), (r, 255, b, a) )
                pixels.putpixel( (i + right, j + down), (r, 255, b, a) )
                pixels.putpixel( (i+left, j+int((up+down)/2)), (r, 255, b, a) )
                pixels.putpixel( (i+right, j+int((up+down)/2)), (r, 255, b, a) )
                pixels.putpixel( (i+int((left+right)/2), j+up), (r, 255, b, a) )
                pixels.putpixel( (i+int((left+right)/2), j+down), (r, 255, b, a) )

        pixels.show()

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write("fr_aspect_x = \"1.000000\"\n")
            output_file.write("fr_aspect_y = \"%3.6f\"\n" % aspect_ratio_n)
            output_file.write("fr_zoom = \"%3.6f\"\n" % zoom)
            output_file.write("fr_center_x = \"%3.6f\"\n" % (100*center_x))
            output_file.write("fr_center_y = \"%3.6f\"\n" % (100*center_y))


if __name__ == '__main__':
	main()
