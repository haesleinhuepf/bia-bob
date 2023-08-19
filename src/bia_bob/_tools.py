from langchain.tools import StructuredTool, tool
from ._machinery import _context
from ._utilities import make_variable_name, find_image

if _context.verbose:
    print("Setting up tools")

@_context.tools.append
@tool
def load_image(filename: str):
    """Useful for loading an image file and storing it under a given variable name."""
    from skimage.io import imread

    if _context.verbose:
        print("loading image", filename)
    image = imread(filename)
    variable_name = make_variable_name(filename)
    _context.variables[variable_name] = image
    return "The image is now stored as " + variable_name


@_context.tools.append
@tool
def load_csv(filename: str):
    """Useful for loading a csv file and storing its as pandas DataFrame under a given variable name."""
    from pandas import read_csv

    if _context.verbose:
        print("loading csv", filename)
    df = read_csv(filename)

    variable_name = make_variable_name(filename)
    _context.variables[variable_name] = df
    return "The csv file is now stored as " + variable_name



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
def gaussian_blur(image_name: str, sigma: float = 1):
    """Useful for removing noise from an image using a simple method: the Gaussian blur."""
    from skimage.filters import gaussian

    if _context.verbose:
        print("denoising (Gaussian blur)", image_name)

    image = find_image(_context.variables, image_name)
    denoised_image = gaussian(image, sigma=sigma)

    denoised_image_name = make_variable_name("denoised_" + image_name)
    _context.variables[denoised_image_name] = denoised_image

    return "The denoised image has been stored as " + denoised_image_name


@_context.tools.append
@tool
def median_filter(image_name: str, radius: int = 1):
    """Useful for removing noise from an image using a simple method: the Gaussian blur."""
    from napari_segment_blobs_and_things_with_membranes import median_filter as nsbatwm_median_filter

    if _context.verbose:
        print("denoising (Median filter)", image_name)

    image = find_image(_context.variables, image_name)
    denoised_image = nsbatwm_median_filter(image, radius=radius)

    denoised_image_name = make_variable_name("denoised_" + image_name)
    _context.variables[denoised_image_name] = denoised_image

    return "The denoised image has been stored as " + denoised_image_name


@_context.tools.append
@tool
def top_hat(image_name: str, radius: int = 10):
    """Useful for removing background from an image using a simple method: the Top-Hat filter."""
    from napari_segment_blobs_and_things_with_membranes import white_tophat

    if _context.verbose:
        print("remove background (Top-Hat)", image_name)

    image = find_image(_context.variables, image_name)
    background_subtracted_image = white_tophat(image, radius=radius)

    background_subtracted_image_name = make_variable_name("removed_background_" + image_name)
    _context.variables[background_subtracted_image_name] = background_subtracted_image

    return "The image with the background removed has been stored as " + background_subtracted_image_name


@_context.tools.append
@tool
def morphological_gradient(image_name: str, radius: int = 1):
    """Useful for enhancing edges in image using a simple method: the Morphological Gradient filter."""
    from napari_segment_blobs_and_things_with_membranes import morphological_gradient as nsbatwm_morphological_gradient

    if _context.verbose:
        print("enhance edges (morphological gradient)", image_name)

    image = find_image(_context.variables, image_name)
    enhanced_edges_image = nsbatwm_morphological_gradient(image, radius=radius)

    enhanced_edges_image_name = make_variable_name("enhanced_edges_" + image_name)
    _context.variables[enhanced_edges_image_name] = enhanced_edges_image

    return "The image with the enhanced edges has been stored as " + enhanced_edges_image_name


@_context.tools.append
@tool
def segment_bright_objects(image_name: str, spot_sigma: float = 4, outline_sigma:float = 2):
    """Useful for segmenting bright objects in an image that has been loaded and stored before using the Voronoi-Otsu-Labeling algorithm."""
    from napari_segment_blobs_and_things_with_membranes import voronoi_otsu_labeling

    if _context.verbose:
        print("segmenting (voronoi_otsu_labeling)", image_name, "using spot_sigma", spot_sigma, "and outline_sigma", outline_sigma)

    image = find_image(_context.variables, image_name)
    label_image = voronoi_otsu_labeling(image, spot_sigma=spot_sigma, outline_sigma=outline_sigma)

    label_image_name = make_variable_name("segmented_" + image_name)
    _context.variables[label_image_name] = label_image

    return f"Voronoi-Otsu-Labeling has been applied using spot_sigma {spot_sigma} and outline_sigma={outline_sigma}. The segmented image has been stored as {label_image_name}."


@_context.tools.append
@tool
def segment_dark_objects_with_bright_borders(image_name: str, spot_sigma: float = 4, outline_sigma:float = 0):
    """Useful for segmenting dark objects with bright borders in an image that has been loaded and stored before using the Local-Minima-Seeded-Watershed algorithm. This might be good for segmenting cells in case membranes are in the image."""
    from napari_segment_blobs_and_things_with_membranes import local_minima_seeded_watershed

    if _context.verbose:
        print("segmenting (local_minima_seeded_watershed)", image_name)

    image = find_image(_context.variables, image_name)
    label_image = local_minima_seeded_watershed(image, spot_sigma=spot_sigma, outline_sigma=outline_sigma)

    label_image_name = "segmented_" + image_name
    _context.variables[make_variable_name(label_image_name)] = label_image

    return f"Local-minima-seeded-watershed has been applied using spot_sigma {spot_sigma} and outline_sigma={outline_sigma}. The segmented image has been stored as {label_image_name}."


@_context.tools.append
@tool
def show_image(image_name: str):
    """Useful for showing an image that has been loaded and stored before.
    """
    import stackview
    from IPython.core.display_functions import display

    if _context.verbose:
        print("showing", image_name)

    image = find_image(_context.variables, image_name)
    display(stackview.insight(image))

    return "The image " + image_name + " has been shown."


@_context.tools.append
@tool
def count_objects(image_name: str):
    """Useful for counting objects in a segmented image that has been loaded and stored before."""
    label_image = find_image(_context.variables, image_name)

    num_labels = label_image.max()
    if _context.verbose:
        print("counting labels in ", image_name, ":", num_labels)

    return f"The label image {image_name} contains {num_labels} labels."


@_context.tools.append
@tool
def slice(image_name: str):
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
def picker(image_name: str):
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
def orthogonal(image_name: str):
    """Useful for interactively inspecting 3D image stacks using orthogonal views."""
    import stackview
    from IPython.core.display_functions import display

    image = find_image(_context.variables, image_name)

    if _context.verbose:
        print("stackview.orthogonal", image_name)

    if len(image.shape) == 3:
        display(stackview.orthogonal(image))
        return f"The image {image_name} has {image.shape[0]} slices."
    else:
        return f"The image {image_name} cannot be sliced."


@_context.tools.append
@tool
def curtain(image1_name: str, image2_name: str, zoom_factor: float = 1.0):
    """Useful for blending one image over another using an interactive curtain."""
    import stackview
    from IPython.core.display_functions import display

    image1 = find_image(_context.variables, image1_name)
    image2 = find_image(_context.variables, image2_name)

    if _context.verbose:
        print("stackview.curtain", image1_name, image2_name)

    display(stackview.curtain(image1, image2, zoom_factor=zoom_factor))
    return f"The images {image1_name} and {image2_name} can now be blended over each other using a curtain."



@_context.tools.append
@tool
def list_tools():
    """Lists all available tools"""

    return "\n".join(list([t.name for t in _context.tools]))



@_context.tools.append
@tool
def list_dataframes():
    """Lists all available dataframes"""
    from ._utilities import is_dataframe

    return "\n".join(list([v for v in _context.variables.keys() if is_dataframe(_context.variables[v])]))


@_context.tools.append
@tool
def list_images():
    """Lists all available images"""
    from ._utilities import is_image

    return "\n".join(list([v for v in _context.variables.keys() if is_image(_context.variables[v])]))





@_context.tools.append
@tool
def list_files_in_folder(folder: str):
    """Lists all files in a folder"""
    import os
    if not os.path.isdir(folder):
        return f"{folder} does not exist."
    return "The files in the folder are " + ",".join(os.listdir(folder))


@_context.tools.append
@StructuredTool.from_function
def multiply_image_with_factor(image_name: str, factor: int):
    """Useful for multiplying the pixel values in an image by an integer value and showing the result"""

    if _context.verbose:
        print(f"multiplying {image_name} by {factor}")
    factor = int(factor)
    image = find_image(_context.variables, image_name)
    result = image * factor

    result_filename = f"multiplied_{image_name}"
    _context.variables[result_filename] = result

    return f"The result is now stored as {result_filename}."


@_context.tools.append
@StructuredTool.from_function
def extract_features(intensity_image_name:str, label_image_name:str,  size : bool = False, intensity : bool = False, perimeter : bool = False, shape : bool = False, position : bool = False, moments : bool = False) -> str:
    """Useful for extracting features from a label image and an intensity image."""
    from napari_skimage_regionprops import regionprops_table

    if _context.verbose:
        print(f"Extracting features (size={size}, intensity={intensity}, perimeter={perimeter}, shape={shape}, position={position}, moments={moments}) from intensity image {intensity_image_name} and label image {label_image_name}.")

    intensity_image = find_image(_context.variables, intensity_image_name)
    label_image = find_image(_context.variables, label_image_name)

    df = regionprops_table(intensity_image, label_image, size=size, intensity=intensity, perimeter=perimeter, shape=shape, position=position, moments=moments)

    result_df_name = make_variable_name(f"extracted_features_{label_image_name}_{intensity_image_name}")
    _context.variables[result_df_name] = df

    return f"The resulting dataframe is stored as '{result_df_name}'"


@_context.tools.append
@StructuredTool.from_function
def show_dataframe(dataframe_name):
    """Useful for showing a dataframe that has been stored before."""
    from IPython.core.display_functions import display
    from ._utilities import find_dataframe

    if _context.verbose:
        print("Showing dataframe", dataframe_name)

    df = find_dataframe(_context.variables, dataframe_name)

    display(df)

    return f"The dataframe {dataframe_name} has been shown."


@_context.tools.append
@StructuredTool.from_function
def list_columns_of_dataframe(dataframe_name):
    """Useful for listing the columns of a dataframe that has been stored before."""
    from ._utilities import find_dataframe

    if _context.verbose:
        print("Listing columns of dataframe", dataframe_name)

    df = find_dataframe(_context.variables, dataframe_name)

    return f"The dataframe has the columns {list(df.columns)}."


@_context.tools.append
@StructuredTool.from_function
def scatterplot_columns_in_dataframe(dataframe:str, first_column:str, second_column:str):
    """Useful for drawing a scatterplot of two columns in a dataframe"""
    from ._utilities import find_dataframe
    from IPython.core.display_functions import display

    if _context.verbose:
        print("Plot command df:", dataframe)
        print("Plot command 1st column:", first_column)
        print("Plot command 2nd column:", second_column)

    df = find_dataframe(_context.variables, dataframe)

    import seaborn
    display(seaborn.jointplot(df, x=first_column, y=second_column))

    return "The scatter plot is shown."


@_context.tools.append
@StructuredTool.from_function
def pairplot_dataframe(dataframe:str, hue_column:str = None):
    """Useful for drawing a pariplot of a dataframe."""
    from ._utilities import find_dataframe
    from IPython.core.display_functions import display

    if _context.verbose:
        print("Plot command df:", dataframe)
        print("Plot command hue_column:", hue_column)

    df = find_dataframe(_context.variables, dataframe)

    import seaborn
    display(seaborn.pairplot(df, hue=hue_column))

    return "The pairplot is shown."


@_context.tools.append
@StructuredTool.from_function
def histogram_of_column_in_dataframe(dataframe:str, column:str):
    """Useful for drawing a histogram of a column in a dataframe."""
    from ._utilities import find_dataframe
    from IPython.core.display_functions import display

    if _context.verbose:
        print("Plot command df:", dataframe)
        print("Plot command column:", column)

    df = find_dataframe(_context.variables, dataframe)

    import seaborn
    display(seaborn.histplot(df, x=column))

    return "The histogram is shown."


@_context.tools.append
@StructuredTool.from_function
def histogram_of_image(image_name:str):
    """Useful for drawing a histogram of an image."""
    from ._utilities import find_image
    import pandas as pd
    from IPython.core.display_functions import display

    if _context.verbose:
        print("Histogram of image", image_name)

    image = find_image(_context.variables, image_name)

    column = "intensity"
    df = pd.DataFrame({column:image.ravel()})

    import seaborn
    display(seaborn.histplot(df, x=column))

    return "The histogram is shown."


@_context.tools.append
@StructuredTool.from_function
def correlation_matrix(dataframe:str):
    """Useful for drawing a correlation matrix of columns in a dataframe."""
    from ._utilities import find_dataframe
    from IPython.core.display_functions import display
    import seaborn

    if _context.verbose:
        print("Plot command df:", dataframe)

    df = find_dataframe(_context.variables, dataframe)


    corr = df.corr()

    display(seaborn.heatmap(corr, annot=False, cmap="coolwarm", vmin=-1, vmax=1))
    return "The correlation matrix is shown."

