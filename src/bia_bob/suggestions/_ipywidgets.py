def suggestions():
    try:
        import ipywidgets
        return """
    ### Build graphical user interfaces
    When asked to build a graphical user interface, use ipywidgets, if no other library is specified.
    """
    except ImportError:
        return ""
