def suggestions():
    return """
    ### Processing images with scikit-image
    
    * Load an image file from disc and store it in a variable:
    ```
    from skimage.io import imread
    image = imread(filename)
    ```
    * Expanding labels by a given radius in a label image works like this:
    ```
    from skimage.segmentation import expand_labels
    expanded_labels = expand_labels(label_image, distance=10)
    ```
    * Measure properties of labels with respect to an image works like this:
    ```
    import pandas as pd
    from skimage.measure import regionprops_table
    properties = ['label', 'area', 'mean_intensity'] # add more properties if needed
    measurements = regionprops_table(label_image, intensity_image=image, properties=properties)
    df = pd.DataFrame(measurements)
    ```
    """