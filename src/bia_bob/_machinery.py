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
        return _context.agent.run(input=line + "\n" + cell)
    if line:
        return _context.agent.run(input=line)
    elif cell:
        return _context.agent.run(input=cell)
    else:
        return "Please enter a question behind %bob"



def init_assistant(variables, temperature=0):
    if _context.verbose:
        print("Initializing assistant")
    from langchain.memory import ConversationBufferMemory
    from langchain.chat_models import ChatOpenAI
    from langchain.agents import initialize_agent
    from langchain.agents import AgentType

    if len(_context.tools) == 0:
        from ._tools import load_image

    _context.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    _context.llm = ChatOpenAI(temperature=temperature)
    _context.agent = initialize_agent(
        _context.tools,
        _context.llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=_context.memory
    )

    _context.variables = variables



init_assistant(globals())
