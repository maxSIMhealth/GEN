import ffmpeg


def read_frame_as_jpeg(in_filename, time):
    """extracts single frame from video based on a specific timestamp"""
    # based on:
    # https://github.com/kkroening/ffmpeg-python/blob/master/examples/read_frame_as_jpeg.py
    out, err = (
        ffmpeg.input(in_filename, ss=time)
        # .filter('select', 'gte(n,{})'.format(frame_num))
        .output("pipe:", vframes=1, format="image2", vcodec="mjpeg").run(
            capture_stdout=True
        )
    )
    return out, err


def crop_image(image):
    """Generates a square cropped image based on its center"""
    width, height = image.size
    left, top, right, bottom = 0, 0, 0, 0

    if width != height:
        if width > height:
            crop = (width - height) / 2
            left = crop
            top = 0
            right = height + crop
            bottom = height
        elif width < height:
            crop = (height - width) / 2
            left = 0
            top = crop
            right = width
            bottom = width + crop

        result = image.crop((left, top, right, bottom))
    else:
        result = image

    return result
