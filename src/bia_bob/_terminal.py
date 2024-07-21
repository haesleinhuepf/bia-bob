def command_line_interface():
    from ._machinery import bob
    import argparse

    parser = argparse.ArgumentParser(description='Process some text commands.')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='All arguments passed to the command')

    args = parser.parse_args()
    full_command = ' '.join(args.args)

    bob(full_command)
