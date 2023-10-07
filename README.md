# bia-bob

BIA `bob` is a Jupyter-based assistant for interacting with data using generated python code. It is based on [OpenAI's API](https://openai.com/blog/openai-api). You need an openai API account to use it.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/screencast.png)

## Usage

You can initialize Bob like this:
```
from bia_bob import bob
```

Afterwards, you can ask Bob questions like this:
```
%bob Load blobs.tif and show it
```

It will then respond with a python code snippet that you can execute ([see full example](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/analysis_workflow.ipynb)):

```
from skimage.io import imread
import stackview

image = imread('blobs.tif')
stackview.insight(image)
```

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/load_and_show_blobs.png)

## Known issues

If you want to ask `bob` a question, you need to put a space before the `?`.

```
%bob What do you know about blobs.tif ?
```

## Installation

You can install `bia-bob` using pip. it is recommended to install it into via conda/mamba environment. If you have never used conda before, please [read this guide first](https://biapol.github.io/blog/mara_lampert/getting_started_with_mambaforge_and_python/readme.html).  

```
mamba create --name bt39 python=3.9 git
mamba activate bt39
pip install bia-bob
```


## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag [@haesleinhuepf].





