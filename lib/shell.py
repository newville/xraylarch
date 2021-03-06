#!/usr/bin/env python

import cmd
import os
import sys
import numpy

from .interpreter import Interpreter
from .inputText import InputText
from .site_config import history_file, show_site_config
from .version import __version__, __date__

BANNER = """  Larch %s  M. Newville, T. Trainor -- %s
  using python %s, numpy %s
"""

class shell(cmd.Cmd):
    ps1    = "larch> "
    ps2    = ".....> "
    def __init__(self,  completekey='tab',   debug=False,
                 stdin=None, stdout=None, quiet=False,
                 banner_msg=None, maxhist=5000):
        self.maxhist = maxhist
        self.debug  = debug
        try:
            import readline
            self.rdline = readline
        except ImportError:
            self.rdline = None
        cmd.Cmd.__init__(self,completekey='tab')
        homedir = os.environ.get('HOME', os.getcwd())

        self.history_written = False
        if self.rdline is not None:
            try:
                self.rdline.read_history_file(history_file)
            except IOError:
                print 'could not read history from ', history_file

        if stdin is not None:   sys.stdin = stdin
        if stdout is not None:  sys.stdout = stdout
        self.stdin = sys.stdin
        self.stdout = sys.stdout

        if banner_msg is None:
            banner_msg = BANNER % (__version__, __date__,
                                   '%i.%i.%i' % sys.version_info[:3],
                                   numpy.__version__)

        if not quiet:
            sys.stdout.write("%s\n" % banner_msg)

        self.larch  = Interpreter()
        self.input  = InputText(prompt=self.ps1, _larch=self.larch)
        self.prompt = self.ps1

        self.larch.run_init_scripts()

    def __del__(self, *args):
        self.__write_history()

    def __write_history(self):
        if self.rdline is None:
            return
        try:
            self.rdline.set_history_length(self.maxhist)
            if history_file is not None and not self.history_written:
                self.rdline.write_history_file(history_file)
        except:
            pass

    def emptyline(self):
        pass

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        return '', '', line

    def larch_execute(self,s_inp):
        self.default(s_inp)

    def do_shell(self, arg):
        os.system(arg)

    def default(self, text):
        text = text.strip()
        if text in ('quit', 'exit', 'EOF'):
            if text in ('quit', 'exit'):
                try:
                    n = self.rdline.get_current_history_length()
                    self.rdline.remove_history_item(n-1)
                except:
                    pass
            self.__write_history()
            self.history_written = True
            return 1

        if text.startswith('help'):
            arg = text[4:]
            if arg.startswith('(') and arg.endswith(')'): arg = arg[1:-1]
            if arg.startswith("'") and arg.endswith("'"): arg = arg[1:-1]
            if arg.startswith('"') and arg.endswith('"'): arg = arg[1:-1]
            text  = "help(%s)"% (repr(arg))
        if text.startswith('!'):
            os.system(text[1:])
        else:
            ret = None
            self.input.put(text, lineno=0)
            self.prompt = self.ps2
            while len(self.input) > 0:
                block, fname, lineno = self.input.get()
                if len(block) == 0:
                    continue
                ret = self.larch.eval(block, fname=fname, lineno=lineno)
                if self.larch.error:
                    err = self.larch.error.pop(0)
                    fname, lineno = err.fname, err.lineno
                    sys.stdout.write("%s\n" % err.get_error()[1])
                    for err in self.larch.error:
                        if self.debug or ((err.fname != fname or err.lineno != lineno)
                                     and err.lineno > 0 and lineno > 0):
                            sys.stdout.write("%s\n" % (err.get_error()[1]))

                    self.input.clear()
                    self.prompt = self.ps1
                    break
                elif ret is not None:
                    sys.stdout.write("%s\n" % repr(ret))
                self.prompt = self.ps1

if __name__ == '__main__':
    fout = open('larch.out', 'w')
    t = shell(debug=True, stdout=fout).cmdloop()
