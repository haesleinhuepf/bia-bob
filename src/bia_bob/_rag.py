def scan_plugins():
    from importlib.metadata import entry_points
    try:
        bia_bob_plugins = entry_points(group='bia_bob_plugins')
    except TypeError:
        all_plugins = entry_points()
        try:
            bia_bob_plugins = all_plugins['bia_bob_plugins']
        except KeyError:
            bia_bob_plugins = []

    additional_instructions = []
    # Iterate over discovered entry points and load them
    for ep in bia_bob_plugins:
        func = ep.load()

        # load instructions from a plugin
        instructions = func()

        print(func.__module__)
        print(eval(func.__module__).__version__)
