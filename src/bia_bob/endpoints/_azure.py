import os
from openai import AzureOpenAI

def prompt_azure():
    """Initialize Azure OpenAI client and return it.

    Returns
    -------
    AzureOpenAI
        An Azure OpenAI client instance configured with the API key,
        version, and endpoint from environment variables.
    """
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    return client
