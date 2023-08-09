class _context():
    tools = []
    llm = None
    agent = None
    variables = None
    verbose = False


from IPython.core.magic import register_line_cell_magic


@register_line_cell_magic
def bob(line: str = None, cell: str = None):
    import re
    if _context.agent is None:
        init_assistant({})

    # print("line", line)
    # print("cell", cell)

    if _context.verbose:
        print("Tools:", len(_context.tools))
        print("Variables:", len(_context.variables.keys()))

    if line and cell:
        result = _context.agent.run(input=line + "\n" + cell)
    elif line:
        result = _context.agent.run(input=line)
    elif cell:
        result = _context.agent.run(input=cell)
    else:
        result = "Please enter a question behind %bob"

    # filter out markdown images from the response
    pattern = r'!\[.*?\]\(.*?\)'
    result = re.sub(pattern, '', result)

    from IPython.display import display, Markdown, Latex
    display(Markdown(result))


def init_assistant(variables, temperature=0):
    if _context.verbose:
        print("Initializing assistant")
    from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.agents import StructuredChatAgent, AgentExecutor, OpenAIFunctionsAgent, initialize_agent, AgentType
    from langchain.prompts import MessagesPlaceholder
    from langchain.schema import SystemMessage

    if len(_context.tools) == 0:
        from ._tools import load_image

    # make the llm
    _context.llm = ChatOpenAI(temperature=temperature)

    # set up the chat memory
    MEMORY_KEY = "chat_history"
    _context.memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)

    system_message = SystemMessage(content="You are a powerful assistant. Answer the human's questions below.")
    agent_kwargs = {
        "system_message": system_message,
        "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)],
    }
    _context.agent = initialize_agent(
        _context.tools,
        _context.llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=_context.verbose,
        agent_kwargs=agent_kwargs,
        memory=_context.memory,
    )
    # store the variables
    _context.variables = variables



init_assistant(globals())
