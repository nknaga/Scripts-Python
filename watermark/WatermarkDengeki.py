# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 18:41:01 2016

@author: Rignak
"""
from PIL import Image
from os import listdir

def InverseFunction(r, g, b, wtmk1_px, wtmk2_px):
    """Try to get the original data of the function from its output
    We suppose that the function is bijective
    f(rt, gt, bt) = r, g, b
    Input:
    r, g, b : int
    wtmk1_px, wtmk2_px : tuple of three int

    Output:
    rt, gt ,bt : int"""
    r_wtmk1, g_wtmk1, b_wtmk1 = wtmk1_px  # Watermark on bright pixel
    r_wtmk2, g_wtmk2, b_wtmk2 = wtmk2_px  # Watermark on dark pixel

    # Negation of colors
    r_wtmk2, g_wtmk2, b_wtmk2 = (255 - r_wtmk2, 255 - g_wtmk2, 255 - b_wtmk2)
    r_wtmk1, g_wtmk1, b_wtmk1 = (255 - r_wtmk1, 255 - g_wtmk1, 255 - b_wtmk1)

    rt, gt, bt = r, g, b
    for i in range(100):
        # The watermark used differs with the brightness
        rt = r+(r_wtmk1*rt/255) - r_wtmk2*((255-rt)/255)
        gt = g+(g_wtmk1*gt/255) - g_wtmk2*((255-gt)/255)
        bt = b+(b_wtmk1*bt/255) - b_wtmk2*((255-bt)/255)
    return int(rt), int(gt), int(bt)


def RemoveWatermark(watermark1, watermark2, picture):
    """Remove the watermark

    Input:
    watermark -- The image containing the watermark
    picture -- The picture to clean

    Output:
    picture -- The picture clean"""
    im = Image.open(picture)
    w, h = im.size  # Get the size of the watermarked picture
    wtmk1 = Image.open(watermark1)
    wtmk2 = Image.open(watermark2)

    w_wtmk, h_wtmk = wtmk1.size

    imr = Image.new("RGB", (w, h))
    for y in range(h):
        imr.putpixel((0,y), im.getpixel((0, y)))
        for x in range(1, w):
            im_pixel = im.getpixel((x, y))
            if h-y > h_wtmk or h-y <= 10 : # No watermark
                imr.putpixel((x, y), im_pixel)
            else:
                x_wtmk = (x-1) % w_wtmk # the coordiante x of the watermark
                y_wtmk = y - h + h_wtmk  # the coordinate y of the watermark
                r, g, b = im_pixel
                f_pixel = InverseFunction(r, g, b,
                                          wtmk1.getpixel((x_wtmk, y_wtmk)),
                                          wtmk2.getpixel((x_wtmk, y_wtmk)))
                imr.putpixel((x, y), f_pixel)

    imr.save(picture[:-4] + '_cleaned.jpg', "JPEG", quality=100)
    wtmk1.close()
    wtmk2.close()
    im.close()
    imr.close()

def Substract(name1, name2):
    """Get the substraction of two image"""
    with Image.open(name1) as pic1:
        w, h = pic1.size
        with Image.open(name2) as pic2:
            imr = Image.new("RGB", (w, h))
            for y in range(h):
                for x in range(w):
                    r1, g1, b1 = pic1.getpixel((x, y))
                    r2, g2, b2 = pic2.getpixel((x, y))
                    imr.putpixel((x, y), (256- (r2-r1),
                                  256 - (g2-g1),256 - (b2-b1)))
    imr.save('Kitchen 2 negatif.jpg', "JPEG", quality=100)


if __name__ == '__main__':
    watermarks = listdir('Watermark')[:2]
    for file in listdir('Images'):
        RemoveWatermark('Watermark/'  + watermarks[0],
                        'Watermark/'  + watermarks[1],
                        'Images/' + file)


