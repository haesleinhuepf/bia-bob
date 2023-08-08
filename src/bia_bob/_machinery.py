class _context():
    tools = []
    llm = None
    agent = None
    variables = None
    verbose = False


from IPython.core.magic import register_line_cell_magic


@register_line_cell_magic
def bob(line: str = None, cell: str = None):
    if _context.agent is None:
        init_assistant({})

    # print("line", line)
    # print("cell", cell)

    if _context.verbose:
        print("Tools:", len(_context.tools))
        print("Variables:", len(_context.variables.keys()))

    if line and cell:
        result = _context.agent.run(input=line + "\n" + cell)
    if line:
        result = _context.agent.run(input=line)
    elif cell:
        result = _context.agent.run(input=cell)
    else:
        result = "Please enter a question behind %bob"

    from IPython.display import display, Markdown, Latex
    display(Markdown(result))



def init_assistant(variables, temperature=0):
    if _context.verbose:
        print("Initializing assistant")
    from langchain.memory import ConversationBufferMemory
    from langchain.chat_models import ChatOpenAI
    from langchain.agents import initialize_agent
    from langchain.agents import AgentType
    from langchain.prompts import MessagesPlaceholder

    if len(_context.tools) == 0:
        from ._tools import load_image

    chat_history = MessagesPlaceholder(variable_name="chat_history")
    _context.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    _context.llm = ChatOpenAI(temperature=temperature)
    _context.agent = initialize_agent(
        _context.tools,
        _context.llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=_context.memory,
        agent_kwargs = {
            "memory_prompts": [chat_history],
            "input_variables": ["input", "agent_scratchpad", "chat_history"]
        }
    )

    _context.variables = variables



init_assistant(globals())
