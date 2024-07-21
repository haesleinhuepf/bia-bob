def suggestions():
    return """
    * Loading files with endings other than `.tif`, `,czi`, `.png` or `.jpg` works like this:
    ```
    from aicsimageio import AICSImage
    aics_image = AICSImage(image_filename)
    image = aics_image.get_image_data("ZYX")
    ```
    """