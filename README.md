# bia-bob

BIA `bob` is a Jupyter-based assistant for interacting with data using large language models which generate python code for Bio-Image Analysis (BIA). 
It can make use of [OpenAI's chatGPT](https://openai.com/blog/openai-api), [Google's Gemini](https://blog.google/technology/ai/google-gemini-ai/), [Anthropic's Claude](https://www.anthropic.com/api), [Helmholtz' blablador](https://helmholtz-blablador.fz-juelich.de/) and [Ollama](https://ollama.com). 
You need an OpenAI API account or a Google Cloud account or a Helmholtz ID account to use it.
Using it with Ollama is free but requires running an Ollama server locally.

`bob` can write short Python code snippets and entire Jupyter notebooks. The default LLM (gpt-4 omni) has vision capabilities and thus, you can show images to `bob` and it will write code for segmenting the structures of interest - in case it recognizes them.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/generate_notebook.gif)

> [!CAUTION]
> When using the OpenAI, Google Gemini, Anthropic or any other endpoint via BiA-Bob, you are bound to the terms of service 
> of the respective companies or organizations.
> The prompts you enter are transferred to their servers and may be processed and stored there. 
> Make sure to not submit any sensitive, confidential or personal data. Also using these services may cost money.

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

### Notebook generation

As shown above, when asking Bob explicitly to generate a notebook, it will put a new notebook file in the current directory with the generated code ([See full example](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/generate_notebooks.ipynb)). You can then open it in Jupyter lab.

### Notebook modification

You can also ask Bob to modify an existing notebook, e.g. to introduce explanatory markdown cells ([See full example](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/modifying_notebooks/modifying_notebooks.ipynb)):

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/modify_notebook.png)

### Bug fixing

Bob can fix simple bugs in code you executed. Just add `%%fix` on top of the cell right after the error happened.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/bug_fixing_mini.gif)

### Code documentation

Using the `%%doc` magic, you can generate documentation for a given code cell.

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/documenting_mini.gif)

### GPU-acceleration

Using the `%%acc` magic, you can replace common image processing functions with GPU-accelerated functions. It is recommended to check if the image processing results remain the same. You can see an example in [this notebook](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/accelerate.ipynb).

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/accelerate.png)


### No-code custom Jupyter Kernel

If installed, you can also choose the BiA-Bob from the Launcher in Jupyter lab:

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/bia-bob-custom-kernel.png)

This will give you a Jupyter kernel that allows you to type in English language instead of code:

![img.png](https://github.com/haesleinhuepf/bia-bob/raw/main/docs/images/bia-bob-custom-kernel3.png)

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

... and install `bia-bob`:

```
pip install bia-bob
```

### Using OpenAI as backend

Create an OpenAI API Key and add it to your environment variables named `OPENAI_API_KEY` as explained on [this page](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

### Using Anthropic / claude

Create an Anthropic API Key and add it to your environment variables named `ANTHROPIC_API_KEY`. Also install this package:

```
pip install anthropic 
```

### Using custom endpoints

Custom endpoints can be used as well if they support the OpenAI API. Examples are [blablador](https://login.helmholtz.de/oauth2-as/oauth2-authz-web-entry) and [ollama](https://ollama.com/).
An example is shown in [this notebook](https://github.com/haesleinhuepf/bia-bob/blob/main/demo/custom_endpoints.ipynb):

For this, just install the openai backend as explained above (tested version: 1.30.1).
* If you want to use ollama and e.g. the `codellama` model, you must run `ollama serve` from a separate terminal and then initialize bob like this:
```
bob.initialize(endpoint='ollama', model='codellama')
```
* If you want to use blablador, which is free for German academics, just get an API key as explained on
[this page](https://sdlaml.pages.jsc.fz-juelich.de/ai/guides/blablador_api_access/) and store it int your environment as `BLABLADOR_API_KEY` variable.
```
bob.initialize(
    endpoint='blablador', 
    model='Mistral-7B-Instruct-v0.2')
```
* Custom end points can be used as well, for example like this:
```
bob.initialize(
    endpoint='http://localhost:11434/v1', 
    api_key='my_key',
    model='codellama')
```

### Using Google gemini 1.5 flash / pro

Create a Google API key and store it in the environment variable `GOOGLE_API_KEY`.

```
mamba install google-generativeai>=0.6.0
```

```
pip install bia-bob
```

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

### BiA-Bob Jupyter kernel (optional)

If you want to use the BiA-Bob Jupyter kernel, please run additionally this command:

```
python -m bia_bob install
```

You can check if it's installed by printing out the list of installed kernels:

```
jupyter kernelspec list
```

And you can uninstall them using this command:

```
jupyter kernelspec uninstall bia-bob
```

## Development

If you want to contribute to `bia-bob`, you can install it in development mode like this:

```
git clone https://github.com/haesleinhuepf/bia-bob.git
cd bia-bob
pip install -e .
```

## Extensibility

If you are maintainer of a Python library and want to make BiA-bob aware of functions in your library, you can extend Bob's knowledge using [entry-points](https://packaging.python.org/en/latest/specifications/entry-points/). Add this to your library `setup.cfg`:
```

[options.entry_points]
bia_bob_plugins =
    plugin1 = your_library._bia_bob_plugins:list_bia_bob_plugins

```

In the above mentioned `_bia_bob_plugins.py` define this function (and feel to rename the function and the Python file):
```
def list_bia_bob_plugins():
    """List of function hints for bia_bob"""
    return """
    * Computes the sum of a and b
    your_library.compute_sum(a:int,b:int) -> int
    
    * Determines the difference between a and b
    your_library.compute_difference(a:int, b:int) -> int
    
    """
```

Note that the syntax should be pretty much as shown above: A bullet point with a short description and a code-snippet just below. 
You can also generate the `list_bia_bob_plugins` function as demonstrated in [this notebook](https://github.com/haesleinhuepf/stackview/blob/c87b59b896aeef9c0b60928b169027d1480c14e9/docs/generate_bia_bob_connector.ipynb).
Please only list the most important functions. If the list of all plugins extending BiA-Bob becomes too long, the prompt will exceed the maximum prompt length.

List of known Python libraries that provide extensions to Bob:
* [pyclesperanto-prototype](https://github.com/clEsperanto/pyclesperanto_prototype)
* [stackview](https://github.com/haesleinhuepf/stackview)

(Feel free to extend this list by sending a pull-request)


## Similar projects

There are similar projects:
* [jupyter-ai](https://github.com/jupyterlab/jupyter-ai)
* [chatGPT-jupyter-extension](https://github.com/jflam/chat-gpt-jupyter-extension)
* [chapyter](https://github.com/chapyter/chapyter/)
* [napari-chatGPT](https://github.com/royerlab/napari-chatgpt)
* [bioimageio-chatbot](https://github.com/bioimage-io/bioimageio-chatbot)

## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag @haesleinhuepf .





