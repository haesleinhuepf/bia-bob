from typing import List, Dict

class FineTuningFromQuestionsAndAnswers:

    def __init__(self, questions_answers: List[Dict]):
        """A fine-tuning helper class that fine-tunes a model using questions and answers provided as a list of
        dictionaries like this:
        ```
        questions_answers = [{
            "question": "How can I open an image",
            "answer": "from skimage.io import imread\nimage = imread(filename)"
            },
            ]
        ```

        Parameters
        ----------
        questions_answers: list of dictionaries with keys "question" and "answer"
        """
        self._training_file = None
        self._fine_tuning_job = None

        self._training_data = []
        for qa in questions_answers:
            self._add_example(qa["question"], qa["answer"])

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
