from langchain.tools import tool
from ._machinery import _context
from ._utilities import make_variable_name, find_image

if _context.verbose:
    print("Setting up tools")

@_context.tools.append
@tool
def load_image(filename: str):
    """Useful for loading and image file and storing it under a given variable name."""
    from skimage.io import imread

    if _context.verbose:
        print("loading", filename)
    image = imread(filename)
    _context.variables[make_variable_name(filename)] = image
    return "The image is now stored as " + filename


@_context.tools.append
@tool
def image_size(filename: str):
    """Useful for telling the size or shape of an image."""
    if _context.verbose:
        print("Determining size of", filename)
    image = find_image(_context.variables, filename)
    return f"The image is {image.shape} pixels large."


@_context.tools.append
@tool
def segment_bright_objects(image_name):
    """Useful for segmenting bright objects in an image that has been loaded and stored before."""
    from napari_segment_blobs_and_things_with_membranes import voronoi_otsu_labeling

    if _context.verbose:
        print("segmenting", image_name)

    image = find_image(_context.variables, image_name)
    label_image = voronoi_otsu_labeling(image, spot_sigma=4)

    label_image_name = "segmented_" + image_name
    _context.variables[make_variable_name(label_image_name)] = label_image

    return "The segmented image has been stored as " + label_image_name


@_context.tools.append
@tool
def show_image(image_name):
    """Useful for showing an image that has been loaded and stored before."""
    import stackview
    from IPython.core.display_functions import display

    if _context.verbose:
        print("showing", image_name)

    image = find_image(_context.variables, image_name)
    display(stackview.insight(image))

    return "The image " + image_name + " is shown above."


@_context.tools.append
@tool
def count_objects(image_name):
    """Useful for counting objects in a segmented image that has been loaded and stored before."""
    label_image = find_image(_context.variables, image_name)

    num_labels = label_image.max()
    if _context.verbose:
        print("counting labels in ", image_name, ":", num_labels)

    return f"The label image {image_name} contains {num_labels} labels."


@_context.tools.append
@tool
def slice(image_name):
    """Useful for slicing a 3d image and going through its slices interactively."""
    import stackview
    from IPython.core.display_functions import display

    image = find_image(_context.variables, image_name)

    if _context.verbose:
        print("stackview.slice", image_name)

    if len(image.shape) == 3:
        display(stackview.slice(image))
        return f"The image {image_name} has {image.shape[0]} slices."
    else:
        return f"The image {image_name} cannot be sliced."

@_context.tools.append
@tool
def list_tools(text):
    """Lists all available tools"""

    return "\n".join(list([t.name for t in _context.tools]))

@_context.tools.append
@tool
def list_files_in_folder(folder):
    """Lists all files in a folder"""
    import os

    return "The files in the folder are " + ",".join(os.listdir(folder))
