from metakernel import MetaKernel
import sys, copy, re


class BiABobKernel(MetaKernel):

    def __init__(self, *args, **kwargs):
        super(BiABobKernel, self).__init__(*args, **kwargs)

        # setup environment for bob
        from bia_bob import bob
        self.variables = []
        bob.initialize(variables=self.variables)

    def do_clear(self):
        self.Print("Clear")
        pass

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        self.Print("Apply")
        pass

    async def do_debug_request(self, msg):
        self.Print("Debug")
        pass

    implementation = 'BiA-Bob'
    implementation_version = '1.0'
    language = 'prompt'
    language_version = '0.1'
    banner = "BiA-Bob"

    language_info = {
        'mimetype': 'text/x-prompt',
        'name': 'prolog',
        'codemirror_mode': {'name': 'prompt'},
    }

    kernel_json = {
        "argv": [sys.executable,
                 "-m", "bia_bob",
                 "-f", "{connection_file}"],
        "display_name": "BiA-Bob",
        "language": "prompt",
        "codemirror_mode": "prompt",
        "name": "BiA-Bob"
    }
    magic_prefixes = dict(magic='%', shell='!', help='?')
    help_suffix = "?"

    def get_usage(self):
        return """Use human language to prompt for tasks"""

    def do_execute_direct(self, code):
        self.Print("Executing", code)
        return None

    def get_completions(self, info):
        token = info["help_obj"]

        return [token + " is great. Explain why", token + " is bad. Explain why"]

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        expr = info["code"]
        if none_on_fail:
            return None
        else:
            return self.do_execute_direct(expr)
