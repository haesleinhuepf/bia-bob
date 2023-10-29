from typing import List

class FineTuningFromNotebooks:

    def __init__(self, notebook_filenames: List[str]):
        """A fine-tuning helper class that fine-tunes a model using the code and text from a list of notebooks.

        Parameters
        ----------
        notebook_filenames: list of notebook filenames (including path)
        """
        self._training_file = None
        self._fine_tuning_job = None
        self._training_data = []

        self._parse_notebooks(notebook_filenames)

    def train(self, wait_for_training_to_finish=False):
        """Fine-tunes the model using the parsed notebooks

        Parameters
        ----------
        wait_for_training_to_finish: if True, wait until training is finished

        Returns
        -------
        Returns the name of the trained model (in case wait_for_training_to_finish is True)
        """
        import os
        import openai
        import tempfile
        import time

        # save training data to a temporary file
        training_data_file_path = os.path.join(tempfile.mkdtemp(), "training_data.jsonl")
        _prepare_data(self._training_data, training_data_file_path)

        # upload and preprocess file
        self._training_file = openai.File.create(
            file=open(training_data_file_path),
            purpose='fine-tune',
        )

        # wait until preprocessing is finished
        while openai.File.retrieve(self._training_file.id).status != "processed":
            time.sleep(30)

        # start fine-tuning
        self._fine_tuning_job = openai.FineTuningJob.create(training_file=self._training_file.id, model="gpt-3.5-turbo")

        # optional: wait until it's finished
        if wait_for_training_to_finish:
            while openai.FineTuningJob.retrieve(self._fine_tuning_job.id).status != "succeeded":
                time.sleep(120)
            return self.trained_model_name()


    def is_trained(self):
        """Returns True if the model is trained, False otherwise"""
        import openai

        if self._training_file is None or self._fine_tuning_job is None:
            return False

        if openai.File.retrieve(self._training_file.id).status != "processed" or \
            openai.FineTuningJob.retrieve(self._fine_tuning_job.id).status != "succeeded":
            return False

        return True


    def trained_model_name(self):
        """Returns the name of the trained model, in case training has finished"""
        import openai
        if self.is_trained():
            job_status = openai.FineTuningJob.retrieve(self._fine_tuning_job.id)

            return job_status.fine_tuned_model
        return None

    def _parse_notebooks(self, notebook_filenames: List[str]):
        """Parses a list of notebooks files and adds the code and text to the training data"""
        for notebook_filename in notebook_filenames:
            self._parse_notebook(notebook_filename)

    def _parse_notebook(self, notebook_path: str):
        """Parses a single notebook file and adds the code and text to the training data"""
        import nbformat

        # Reading the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        metadata = notebook['metadata']

        last_text = ""
        last_code = ""

        first_text = ""
        all_code = ""

        # go through all cells
        cells = notebook['cells']
        for cell in cells:
            cell_type = cell['cell_type']
            if cell_type == 'code':
                # Access code cell
                last_code = last_code + "\n\n" + cell['source']
            elif cell_type == 'markdown':

                # we add the last code block and the text before to the training data
                if len(last_code) > 0:
                    # remove inital line breaks, tabs and spaces
                    while last_code[0] in ["\n", "\t", " "]:
                        last_code = last_code[1:]
                        if len(last_code) == 0:
                            break

                    # print("----", last_code[:6])
                    if not (last_code.startswith("from") or last_code.startswith("import")):
                        # we skip the first block which contains a lot of introductory text and import statements
                        self._add_conversation_step(last_text, last_code)

                        # but we keep it for later
                        first_text = last_text
                    all_code = all_code + "\n\n" + last_code
                    last_code = ""
                    last_text = ""

                # Access markdown cell
                last_text = last_text + "\n\n" + cell['source']

        # We also add the very first text block and all code to the training data
        self._add_conversation_step(first_text, all_code)



    def _add_conversation_step(self, text, code):
        """Adds a conversation step (text and corresponding code) to the training data"""
        if len(code) == 0:
            return

        self._add_example(f"""
What can be done do achieve the following?

{text}
""", f"""
This is Python code for doing this:

```python
{code}
```
    """)

    def _add_example(self, input, output):
        self._training_data.append(
            {
                "messages": [
                    {"role": "system", "content": """
    You are a chatbot with strong bio-image analysis expertise.
    You are an expert python programmer. 
    The code you produce will be executed from a Jupyter notebook.
    """},
                    {"role": "user", "content": input},
                    {"role": "assistant", "content": output}
                ]
            })

def _prepare_data(dictionary_data, final_file_name):
    """Writes a list of dictionaries to a jsonl file"""
    import json
    with open(final_file_name, 'w') as outfile:
        for entry in dictionary_data:
            json.dump(entry, outfile)
            outfile.write('\n')
