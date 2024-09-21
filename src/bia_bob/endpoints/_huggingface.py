def generate_response_from_huggingface(model: str, system_prompt: str, user_prompt: str, chat_history, image=None,
                                  base_url:str=None, api_key:str=None, vision_model:str = None, vision_system_prompt:str = None):
    """A prompt helper function that sends a message to a local
    huggingface model and returns only the text response.
    """
    if image is not None:
        raise NotImplementedError("Vision models are not supported via the Huggingface endpoint (yet)")

    from .._machinery import Context

    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        pipeline,
    )
    import torch

    if Context.model is None or "Pipeline" not in str(type(Context.model)):
        hf_model = AutoModelForCausalLM.from_pretrained(
            model,
            device_map="auto"
        )
        hf_tokenizer = AutoTokenizer.from_pretrained(model)

        Context.model = pipeline(
            "text-generation",
            model=hf_model,
            tokenizer=hf_tokenizer,
            torch_dtype=torch.float16,
            device_map="auto",
        )
    reply = Context.model(system_prompt + "\n\n" + user_prompt, max_new_tokens=4096)[0]["generated_text"]

    user_message = [{"role": "user", "content": user_prompt}]
    assistant_message = [{"role": "assistant", "content": reply}]

    Context.chat += user_message + assistant_message

    return reply
