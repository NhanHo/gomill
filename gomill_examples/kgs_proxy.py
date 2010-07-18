"""GTP proxy for use with kgsGtp.

This supports saving a game record after each game, if the underlying engine
supports gomill-savesgf.

"""
import os
import sys

from gomill import gtp_engine
from gomill import gtp_controller
from gomill import gtp_proxy
from gomill.gtp_controller import GtpEngineError

# FIXME: Get from command line
SGF_DIR = "/home/mjw/gotourn/kgs/games"
FILENAME_TEMPLATE = "%04d.sgf"

class Kgs_proxy(object):
    """GTP proxy for use with kgsGtp."""
    def __init__(self, command_line):
        self.sgf_dir = SGF_DIR
        self.check_sgf_dir()
        channel = gtp_controller.Subprocess_gtp_channel(command_line)
        controller = gtp_controller.Gtp_controller_protocol()
        controller.add_channel("sub", channel)
        self.proxy = gtp_proxy.Gtp_proxy('sub', controller)
        self.proxy.engine.add_command('kgs-game_over', self.handle_game_over)
        self.proxy.engine.add_command('genmove', self.handle_genmove)
        self.do_savesgf = self.proxy.back_end_has_command("gomill-savesgf")
        # Colour that we appear to be playing
        self.my_colour = None
        self.initialise_name()

    def log(self, s):
        print >>sys.stderr, s

    def run(self):
        gtp_engine.run_interactive_gtp_session(self.proxy.engine)

    def initialise_name(self):
        def shorten_version(name, version):
            """Clean up redundant version strings."""
            if version.lower().startswith(name.lower()):
                version = version[len(name):].lstrip()
            # For MoGo's stupidly long version string
            a, b, c = version.partition(". Please read http:")
            if b:
                version = a
            return version[:32].rstrip()

        self.my_name = None
        try:
            self.my_name = self.proxy.pass_command("name", [])
            version = self.proxy.pass_command("version", [])
            version = shorten_version(self.my_name, version)
            self.my_name += ":" + version
        except GtpEngineError:
            pass

    def handle_genmove(self, args):
        self.my_colour = gtp_engine.interpret_colour(args[0])
        return self.proxy.pass_command("genmove", args)

    def check_sgf_dir(self):
        if not os.path.isdir(self.sgf_dir):
            sys.exit("kgs_proxy: can't find save game directory %s" %
                     self.sgf_dir)

    def choose_filename(self, existing):
        existing = set(existing)
        for i in xrange(10000):
            filename = FILENAME_TEMPLATE % i
            if filename not in existing:
                return filename
        raise StandardError("too many sgf files")

    def handle_game_over(self, args):
        """Handler for kgs-game_over.

        kgsGtp doesn't send any arguments, so we don't know the result.

        """
        def escape_for_savesgf(s):
            return s.replace("\\", "\\\\").replace(" ", "\\ ")

        if self.do_savesgf:
            filename = self.choose_filename(os.listdir(self.sgf_dir))
            pathname = os.path.join(self.sgf_dir, filename)
            self.log("kgs_proxy: saving game record to %s" % pathname)
            args = [pathname]
            if self.my_colour is not None and self.my_name is not None:
                args.append("P%s=%s" % (self.my_colour.upper(),
                                        escape_for_savesgf(self.my_name)))
            self.proxy.pass_command("gomill-savesgf", args)


def main():
    kgs_proxy = Kgs_proxy(sys.argv[1:])
    kgs_proxy.run()

if __name__ == "__main__":
    main()
