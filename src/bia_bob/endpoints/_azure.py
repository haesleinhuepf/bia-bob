import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient

def prompt_azure(base_url: str = None, api_key: str = None) -> ChatCompletionsClient:
    """Initialize Azure ChatCompletionsClient with environment variables or provided parameters.

    Parameters
    ----------
    base_url : str, optional
        The endpoint URL for Azure, by default retrieved from environment variables.
    api_key : str, optional
        The API key for Azure, by default retrieved from environment variables.

    Returns
    -------
    ChatCompletionsClient
        Configured Azure ChatCompletionsClient instance.
    """
    if base_url is None:
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT")

    if api_key is None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")

    client = ChatCompletionsClient(
        endpoint=base_url,
        credential=AzureKeyCredential(api_key)
    )
    return client
