# bia-tischi

BIA `tischi` is a Jupyter-based assistant for interacting with data using generated python code. 


## Known issues

If you want to ask `tischi` a question, you need to put a space before the `?`.

```
%tischi What do you know about blobs.gif ?
```

## Installation

You can install `bia-tischi` using pip. it is recommended to install it into via conda/mamba environment. If you have never used conda before, please [read this guide first](https://biapol.github.io/blog/mara_lampert/getting_started_with_mambaforge_and_python/readme.html).  

```
mamba create --name bt39 python=3.9 git
mamba activate bt39
git clone https://github.com/haesleinhuepf/bia-tischi.git
cd bia-tischi
pip install -e .
```


## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag [@haesleinhuepf].





