from metakernel import MetaKernel
import sys, os


class BiABobKernel(MetaKernel):
    implementation = 'BiA-Bob'
    implementation_version = '1.0'
    language = 'prompt'
    language_version = '0.1'
    banner = "BiA-Bob"

    language_info = {
        'mimetype': 'text/x-prompt',
        'name': 'prompt',
        'codemirror_mode': {'name': 'prompt'},
    }

    kernel_json = {
        "argv": [sys.executable,
                 "-m", "bia_bob",
                 "-f", "{connection_file}"],
        "display_name": "BiA-Bob (gpt-4-1106-preview)",
        "language": "prompt",
        "codemirror_mode": "prompt",
        "name": "BiA-Bob-gpt-4-1106-preview",
        "logo": str(os.path.abspath(__file__)) + "/images/logo-64x64.png"
    }
    model = 'gpt-4-1106-preview'
    magic_prefixes = dict(magic='%', shell='!', help='?')
    help_suffix = "?"

    def __init__(self, *args, **kwargs):
        super(BiABobKernel, self).__init__(*args, **kwargs)

        # setup environment for bob
        from bia_bob import bob
        from bia_bob._machinery import Context
        self.variables = {}
        bob.initialize(model=self.model, variables=self.variables)

        # We filter out some libraries because we have custom display capabilities in this custom kernel
        Context.libraries = [l for l in Context.libraries if l != "stackview"]

        # make sure the results are as reproducible as they get
        Context.seed = 42
        Context.temperature = 0.01

    def get_usage(self):
        return """
        Use human language to prompt for tasks interacting with data.
        Documentation: https://github.com/haesleinhuepf/bia-bob
        """

    def custom_display(self, obj):
        """This function makes sure that image and text output are shown properly."""
        import stackview
        if hasattr(obj, "shape") and hasattr(obj, "dtype"):
            self.Display(stackview.insight(obj))
        else:
            self.Display(obj)

    def custom_plt_show(self):
        """This function makes sure the output of matplotlib gets shown properly."""
        from stackview._static_view import _plt_to_png, _png_to_html
        from IPython.core.display import HTML
        html = _png_to_html(_plt_to_png())
        self.custom_display(HTML(html))

    def do_execute_direct(self, prompt):
        """This function is called when the user executes a cell with a given prompt."""
        prompt = prompt + """ 
        For showing and displaying images or dataframes, use the `display()` function. 
        Instead of `plt.show()` always use `plt_show()`. Make sure this function is called after plotting things with matplotlib.
        Do not forget to provide the code block by the very end.
        """
        self.variables['display'] = self.custom_display
        self.variables['plt_show'] = self.custom_plt_show
        self.variables['print'] = self.custom_display

        self.prompt_chatgpt(prompt)

        return None

    def get_completions(self, info):
        """Auto-completion. Todo: Fill with useful content"""
        token = info["help_obj"]
        return [token + " is great. Explain why", token + " is bad. Explain why"]

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        """This function is called when a code block ends with ? We forward this to a normal cell execution"""
        expr = info["code"]
        if none_on_fail:
            return None
        else:
            return self.do_execute_direct(expr)

    def prompt_chatgpt(self, prompt:str):
        """Submit a prompt to chatGPT, print out text response and execute code."""
        from ._utilities import generate_response_to_user
        from ._machinery import Context
        from IPython.display import Markdown

        user_input = prompt
        image = None

        if user_input is None:
            return

        # generate the response
        code, text = generate_response_to_user(Context.model, user_input, image)

        # print out explanation
        if text is not None:
            self.Display(Markdown(text))

        if code is not None:
            # out of Jupyter environment, e.g. in kernel execution
            self.display_code(code)
            try:
                exec(code, Context.variables)
            except Exception as e:
                import traceback
                self.Print("An exception occurred:", e)
                self.Print(traceback.format_exc())

    def display_code(self, code):
        """Display code content in the notebook."""
        from IPython.core.display import HTML

        self.custom_display(HTML(f"""
        <details>
        <summary> Show code </summary>
        <pre>
{code}
        </pre>
        </details>
        """))

    # not sure if those are strictly necessary: They were added by the IDE
    def do_clear(self):
        self.Print("Clear")
        pass

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        self.Print("Apply")
        pass

    async def do_debug_request(self, msg):
        self.Print("Debug")
        pass
