# Start from the Jupyter minimal image with Python 3.11
FROM jupyter/minimal-notebook:python-3.11

# Switch back to the notebook user
USER $NB_UID

# Copy bia-bob environment file
COPY environment.yml /tmp/environment.yml

# Update the base conda environment
RUN mamba env update -n base -f /tmp/environment.yml && mamba clean -afy

# install Ollama system-wide
USER root
RUN curl -fsSL https://ollama.com/install.sh | sh

USER $NB_UID
COPY --chown=${NB_UID}:${NB_GID} binder/README.ipynb "${HOME}"/README.ipynb

RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"