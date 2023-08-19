# bia-bob

BIA Bob is a Jupyter-based assistant for interacting with image data and for working on Bio-image Analysis tasks.
It is based on [LangChain](https://python.langchain.com/docs/get_started/introduction.html) and [OpenAI's API](https://openai.com/blog/openai-api). You need an openai API account to use it.

Trailer:

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/bia_bob_trailer.gif)

Note: Bob is currently in an early alpha stage. It is not very smart yet and only knows some basic image processing algorithms. 
Feedback and contributions are very welcome!

## Usage

You can initialize Bob like this:
```
from bia_bob import bob
```

In case you want it to be aware of all your variables, call this additionally:
```
bob.initialize(globals())
```

Afterwards, you can ask Bob questions like this:
```
%bob Load blobs.tif and show it
```

Or like this:
```
%%bob
Please load the image blobs.tif,
segment bright objects in it, 
count them and 
show the segmentation result.
```

You can also ask Bob about available tools:
```
%bob list tools
```

Detailed examples of how to interact with Bob are given in these notebooks:
* [Basic usage](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/basic_demo.ipynb)
* [Speech recognition](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/speech_recognition.ipynb)
* [Complete Bio-image Analysis Workflow](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/complete_workflow.ipynb)
* [Accessing variables](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/globals.ipynb)
* [Image Filtering](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/image_filtering.ipynb)
* [Choosing image segmentation algorithms](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/segmentation_algorithms.ipynb)
* [Asking Bob what it does](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/asking_bob_what_it_does.ipynb)
* [Listing tools](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/listing_tools.ipynb)
* [Browsing folders](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/browsing_folders.ipynb)
* [Interactive image stack viewing](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/interactive_stackview.ipynb)
* [For developers](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/for_developers.ipynb)
* [Extensibility](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/extensibility.ipynb)

## Example gallery

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/load_and_show.png)

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/correlation_matrix.png)

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/curtain.png)

![img_1.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/slice.png)

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/count_blobs.png)

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/edge_detection.png)

## Known issues

If you want to ask Bob a question, you need to put a space before the `?`.

```
What do you know about blobs.gif ?
```

## Installation

```
pip install bia-bob
```


## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag [@haesleinhuepf].





