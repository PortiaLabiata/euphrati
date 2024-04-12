from PIL import Image

def load(path_image, path_watermark):
    return Image.open(path_image), Image.open(path_watermark)

def resize(img, watermark, height_perc=7.5, width_perc=50, h_use=True):
    '''
    Creates watermark with specified width or height (in % of image). Uses thumbnail function, so there are some
    quality losses. I chose Hamming resampling method, but I have no idea what I am doing.
    '''
    h = img.height
    w = img.width
    if h_use:
        h = height_perc/100*h
    else:
        w = width_perc/100*w
    watermark.thumbnail((w, h), resample=Image.Resampling.HAMMING)

def paste_watermark(image, watermark, location='rb'):
    '''
    Pastes ALREADY RESIZED watermark into image. Location choice is possible.
    '''
    box = (image.width-watermark.width, image.height-watermark.height)
    if location == 'rb':
        pass
    elif location == 'lb':
        box = (0, image.height-watermark.height)
    elif location == 'rt':
        box = (image.width-watermark.width, 0)
    elif location == 'lt':
        box = (0, 0)
    else:
        raise Exception('Invalid location, dude!')
    image.paste(watermark, box, watermark)

if __name__ == '__main__':
    img, wmk = load('./lain.png', './watermark.png')
    resize(img, wmk)
    paste_watermark(img, wmk)
    img.save('img.png')
    wmk.save('wmk.png')
