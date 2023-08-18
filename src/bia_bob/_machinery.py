class _context():
    tools = []
    llm = None
    agent = None
    variables = None
    voice = None
    verbose = False


from IPython.core.magic import register_line_cell_magic


@register_line_cell_magic
def bob(line: str = None, cell: str = None):
    from IPython.display import display, Markdown
    if _context.agent is None:
        init_assistant({})

    # print("line", line)
    # print("cell", cell)

    if _context.verbose:
        print("Tools:", len(_context.tools))
        print("Variables:", len(_context.variables.keys()))

    if line and cell:
        prompt = line + "\n" + cell
    elif line:
        prompt = line
    elif cell:
        prompt = cell
    else:
        display("Please enter a question behind %bob")
        return ""

    # why? https://github.com/haesleinhuepf/bia-bob/issues/13
    if not prompt.strip().endswith("?"):
        prompt = prompt + "\nSummarize the answers in maximum two sentences."

    result = _context.agent.run(input=prompt)

    display(Markdown(result))
    if _context.voice:
        from ._speak import _speak_out
        _speak_out(result)


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

    system_message = SystemMessage(content="""
    You never produce sample data.
    You never print out dataframes.
    Answer the human's questions below and keep your answers short.
    """)
    agent_kwargs = {
        "system_message": system_message,
        "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)]
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

def add_function_tool(callable):
    """
    Adds a function tool to the agent.

    The given callable must have parameters of type string, int and float.
    It must have a docstring that describes the function, ideally explaining what the function is useful for using
    terms from the target audience.

    After calling this function, the agent is re-initialized.
    """
    from langchain.tools import StructuredTool

    _context.tools.append(StructuredTool.from_function(callable))

    if _context.agent is not None:
        init_assistant(_context.variables)