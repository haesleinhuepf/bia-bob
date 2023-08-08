class _context():
    tools = []
    llm = None
    chat_agent = None
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
    elif line:
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

    if len(_context.tools) == 0:
        from ._tools import load_image

    _context.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # set up the prompt
    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = StructuredChatAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    memory = ConversationBufferMemory(memory_key="chat_history")

    # make the agent executor
    _context.llm = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
    _context.chat_agent = StructuredChatAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    _context.agent = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    # store the variables
    _context.variables = variables



init_assistant(globals())
