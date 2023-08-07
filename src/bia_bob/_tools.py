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
def gaussian_blur(image_name):
    """Useful for removing noise from an image using a simple method: the Gaussian blur."""
    from skimage.filters import gaussian

    if _context.verbose:
        print("denoising (Gaussian blur)", image_name)

    image = find_image(_context.variables, image_name)
    denoised_image = gaussian(image, sigma=1)

    denoised_image_name = make_variable_name("denoised_" + image_name)
    _context.variables[denoised_image_name] = denoised_image

    return "The denoised image has been stored as " + denoised_image_name


@_context.tools.append
@tool
def median_filter(image_name):
    """Useful for removing noise from an image using a simple method: the Gaussian blur."""
    from napari_segment_blobs_and_things_with_membranes import median_filter as nsbatwm_median_filter

    if _context.verbose:
        print("denoising (Median filter)", image_name)

    image = find_image(_context.variables, image_name)
    denoised_image = nsbatwm_median_filter(image, radius=1)

    denoised_image_name = make_variable_name("denoised_" + image_name)
    _context.variables[denoised_image_name] = denoised_image

    return "The denoised image has been stored as " + denoised_image_name


@_context.tools.append
@tool
def top_hat(image_name):
    """Useful for removing background from an image using a simple method: the Top-Hat filter."""
    from napari_segment_blobs_and_things_with_membranes import white_tophat

    if _context.verbose:
        print("remove background (Top-Hat)", image_name)

    image = find_image(_context.variables, image_name)
    background_subtracted_image = white_tophat(image, radius=10)

    background_subtracted_image_name = make_variable_name("removed_background_" + image_name)
    _context.variables[background_subtracted_image_name] = background_subtracted_image

    return "The image with the background removed has been stored as " + background_subtracted_image_name


@_context.tools.append
@tool
def morphological_gradient(image_name):
    """Useful for enhancing edges in image using a simple method: the Morphological Gradient filter."""
    from napari_segment_blobs_and_things_with_membranes import morphological_gradient as nsbatwm_morphological_gradient

    if _context.verbose:
        print("enhance edges (morphological gradient)", image_name)

    image = find_image(_context.variables, image_name)
    enhanced_edges_image = nsbatwm_morphological_gradient(image, radius=1)

    enhanced_edges_image_name = make_variable_name("enhanced_edges_" + image_name)
    _context.variables[enhanced_edges_image_name] = enhanced_edges_image

    return "The image with the enhanced edges has been stored as " + enhanced_edges_image_name


@_context.tools.append
@tool
def segment_bright_objects(image_name):
    """Useful for segmenting bright objects in an image that has been loaded and stored before using the Voronoi-Otsu-Labeling algorithm."""
    from napari_segment_blobs_and_things_with_membranes import voronoi_otsu_labeling

    if _context.verbose:
        print("segmenting (voronoi_otsu_labeling)", image_name)

    image = find_image(_context.variables, image_name)
    label_image = voronoi_otsu_labeling(image, spot_sigma=4)

    label_image_name = "segmented_" + image_name
    _context.variables[make_variable_name(label_image_name)] = label_image

    return "The segmented image has been stored as " + label_image_name


@_context.tools.append
@tool
def segment_dark_objects_with_bright_borders(image_name):
    """Useful for segmenting dark objects with bright borders in an image that has been loaded and stored before using the Local-Minima-Seeded-Watershed algorithm. This might be good for segmenting cells in case membranes are in the image."""
    from napari_segment_blobs_and_things_with_membranes import local_minima_seeded_watershed

    if _context.verbose:
        print("segmenting (local_minima_seeded_watershed)", image_name)

    image = find_image(_context.variables, image_name)
    label_image = local_minima_seeded_watershed(image, spot_sigma=10)

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
def picker(image_name):
    """Useful for interactively inspecting images and picking pixel intensities."""
    import stackview
    from IPython.core.display_functions import display

    image = find_image(_context.variables, image_name)

    if _context.verbose:
        print("stackview.slice", image_name)

    if len(image.shape) == 3:
        display(stackview.picker(image))
        return f"The image {image_name} has {image.shape[0]} slices."
    else:
        return f"The image {image_name} cannot be sliced."


@_context.tools.append
@tool
def orthogonal(image_name):
    """Useful for interactively inspecting 3D image stacks using orthogonal views."""
    import stackview
    from IPython.core.display_functions import display

    image = find_image(_context.variables, image_name)

    if _context.verbose:
        print("stackview.slice", image_name)

    if len(image.shape) == 3:
        display(stackview.orthogonal(image))
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



