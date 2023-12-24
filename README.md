# bia-bob

BIA `bob` is a Jupyter-based assistant for interacting with data using large language models which generate python code. 
It can make use of [OpenAI's chatGPT API](https://openai.com/blog/openai-api) or [Google's Vertex AI API](https://cloud.google.com/vertex-ai?hl=en) and [Gemini](https://blog.google/technology/ai/google-gemini-ai/). 
You need an OpenAI API account or a Google Cloud account to use it.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/screencast.gif)

## Usage

You can initialize `bob` like this:
```
from bia_bob import bob
```

### Code generation

You can ask Bob to generate code like this:
```
%bob Load blobs.tif and show it
```

It will then respond with a python code snippet that you can execute ([see full example](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/analysis_workflow.ipynb)):

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/load_and_show_blobs.png)

### Bug fixing

Bob can fix simple bugs in code you executed. Just add `%%fix` on top of the cell right after the error happened.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/bug_fixing_mini.gif)

### Code documentation

Using the `%%doc` magic, you can generate documentation for a given code cell.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/documenting_mini.gif)

### Example notebooks

* [Basic demo](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/basic_demo.ipynb)
* [Bio-image analysis workflow](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/analysis_workflow.ipynb)
* [Choosing a model](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/choose_model.ipynb)
* [Using Gemini and chatGPT altenating](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/gemini.ipynb)
* [Interpreting images](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/vision.ipynb)
* [Documenting code](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/documenting_code.ipynb)
* [Fixing bugs](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/bug_fixing.ipynb)
* [Graphical user interfaces](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/gui_plots.ipynb)
* [Exploring tabular data](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/videogame_sales.ipynb)

## Known issues

If you want to ask `bob` a question, you need to put a space before the `?`.

```
%bob What do you know about blobs.tif ?
```

## Installation

You can install `bia-bob` using pip. it is recommended to install it into via conda/mamba environment. If you have never used conda before, please [read this guide first](https://biapol.github.io/blog/mara_lampert/getting_started_with_mambaforge_and_python/readme.html).  

It is recommended to install `bia-bob` in a conda-environment together with useful tools for bio-image analysis. 

```
mamba env create -f https://github.com/haesleinhuepf/bia-bob/raw/main/environment.yml
```

You can then activate this environment...

```
mamba activate bob_env
```

... and install `bia-bob`.

### Using OpenAI as backend
```
pip install bia-bob openai
```
(Recommended openai version >= 1.2.0)

Create an OpenAI API Key and add it to your environment variables as explained on [this page](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

### Using Google's Cloud AI API as backend

```
pip install bia-bob google-cloud-aiplatform
```
(Recommended google-cloud-aiplatform version >= 1.38.1)

To make use of the Google Cloud API, you need to create a Google Cloud account [here](https://console.cloud.google.com/welcome/) and
a project within the Google cloud (for billing) [here](https://console.cloud.google.com/projectcreate). 
You need to store authentication details locally as explained [here](https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev). 
This requires installing [Google Cloud CLI](https://cloud.google.com/sdk/docs/install). In very short: run the installer and when asked, activate the "Run gcloud init' checkbox. Or run 'gcloud init' from the terminal yourself. Restart the terminal window.
After installing Google Cloud CLI, start a terminal and authenticate using: 
```
gcloud auth application-default login
```
Follow the instructions in the browser. Enter your Project ID (not the name). If it worked the terminal should approximately look like this:

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/gcloud_auth.png)

## Development

If you want to contribute to `bia-bob`, you can install it in development mode like this:

```
git clone https://github.com/haesleinhuepf/bia-bob.git
cd bia-bob
pip install -e .
```

## Similar projects

There are similar projects:
* [jupyter-ai](https://github.com/jupyterlab/jupyter-ai)
* [napari-chatGPT](https://github.com/royerlab/napari-chatgpt)
* [bioimageio-chatbot](https://github.com/bioimage-io/bioimageio-chatbot)

## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag @haesleinhuepf .





