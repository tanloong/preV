import sys
from code import InteractiveConsole
from textwrap import dedent as _dedent

from .consts import __version__


class PrevInteractiveConsole(InteractiveConsole):
    PS1 = "prev> "
    PS2 = "  ... "

    def __init__(self, runner):
        self.runner = runner
        self.runner.prepare_interact()
        sys.ps1 = self.PS1
        sys.ps2 = self.PS2
        super().__init__()

    def do_help(self, arg): ...

    def runsource(self, source, filename="<input>", symbol="single"):
        if not source or source is False:
            return
        if source[0] == ".":
            if line := source[1:].strip():
                try:
                    cmd, arg = line.split(maxsplit=1)
                except ValueError:
                    cmd, arg = line, None
                if (func := getattr(self, "do_" + cmd, None)) is not None:
                    func(arg)
                else:
                    self.write(
                        f'Error: unknown command or invalid arguments:  "{line}". Enter ".help" for help\n'
                    )
        else:
            self.runner.run_on_text(source)

    def push(self, line):
        if not line or line.isspace():
            source = "\n".join(self.buffer)
            self.runsource(source, self.filename)
            self.resetbuffer()
            return False
        else:
            self.buffer.append(line)
            return True

    def interact(self):
        if sys.platform == "win32" and "idlelib.run" not in sys.modules:
            eofkey = "CTRL-Z"
        else:
            eofkey = "CTRL-D"
        banner = _dedent(f"""
            PREV version {__version__}
            Type text, Type Enter to input multi-line text, Type Enter on a blank line to commit.
            Type ".help" for usage hints; type ".quit" or {eofkey} to quit.
        """).strip()
        super().interact(banner=banner, exitmsg="")
