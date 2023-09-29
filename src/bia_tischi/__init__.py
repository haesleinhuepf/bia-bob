__version__ = "0.1.0"

__all__ = (
    )

from ._machinery import bob, xbob, cbob, vars, populate_next_cell, init_agent

bob.initialize = init_agent
bob.__version__ = __version__

xbob.initialize = init_agent
xbob.__version__ = __version__

cbob.initialize = init_agent
cbob.__version__ = __version__