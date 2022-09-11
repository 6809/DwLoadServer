import argparse
import logging
import shutil
from pathlib import Path

import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from dev_shell.base_cmd2_app import DevShellBaseApp, run_cmd2_app
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.config import DevShellConfig
from dev_shell.utils.colorful import bright_yellow
from dev_shell.utils.subprocess_utils import verbose_check_call
from dragonlib.utils.logging_utils import LOG_LEVELS, setup_logging
from poetry_publish.publish import poetry_publish

import dwload_server
from dwload_server.server_becker import run_becker_server
from dwload_server.server_serial import run_serial_server


PACKAGE_ROOT = Path(dwload_server.__file__).parent.parent
DWLOAD_DEMO_FILES = PACKAGE_ROOT / 'dwload-demo-files'
if not DWLOAD_DEMO_FILES.is_dir():
    raise IsADirectoryError(DWLOAD_DEMO_FILES)


@cmd2.with_default_category('DWLOAD Server Commands')
class DwLoadCommandSet(DevShellBaseCommandSet):

    run_parser = Cmd2ArgumentParser()
    run_parser.add_argument('--root-dir', type=Path, default=Path('~/dwload-files').expanduser())
    run_parser.add_argument(
        '--log-level',
        type=int,
        choices=LOG_LEVELS,
        default=logging.INFO,
        help=(
            "Logging level:"
            " 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL"
            " (default: %(default)s)"
        ),
    )

    interface_argparser = run_parser.add_subparsers(title="Interface")
    becker_parser = interface_argparser.add_parser(
        name="becker",
        help="Use the Becker interface",
    )
    becker_parser.add_argument(
        '--ip',
        default="127.0.0.1",
        help="Port number (default: %(default)s)",
    )
    becker_parser.add_argument(
        '--port',
        type=int,
        default=65504,
        help="Port number (default: %(default)s)",
    )
    serial_parser = interface_argparser.add_parser(
        name="serial",
        help="Use the serial interface",
        # epilog="e.g.: '%s --machine CoCo2b' run" % self.parser.prog
    )
    serial_parser.add_argument(
        '--port',
        default='/dev/ttyUSB0',
        help=(
            "Serial port."
            " Windows e.g.: 'COM3'"
            " - Linux e.g.: '/dev/ttyUSB0'"
            " (default: %(default)s)"
        ),
    )

    @with_argparser(run_parser)
    def do_run(self, args: argparse.Namespace):
        root_dir: Path = args.root_dir
        print(f'root dir: "{root_dir}"')
        if not root_dir.exists():
            print('Create root dir...')
            root_dir.mkdir()
            autoload_src_path = PACKAGE_ROOT / 'dwload-demo-files' / 'AUTOLOAD.DWL.py'
            if not autoload_src_path.is_file():
                raise FileNotFoundError(autoload_src_path)
            print(f'Copy {autoload_src_path} to root dir...')
            shutil.copy(src=autoload_src_path, dst=root_dir / autoload_src_path.name)

        print(f'log level: {args.log_level!r}')

        interface = args.cmd2_statement.get()
        print(f'Interface: {interface!r}')
        if interface == 'serial':
            print(f'Serial port: {args.port}')
            setup_logging(level=args.log_level)
            run_serial_server(args.root_dir, port=args.port)
        elif interface == 'becker':
            print(f'IP: {args.ip!r}')
            print(f'port: {args.port}')
            setup_logging(level=args.log_level)
            run_becker_server(args.root_dir, ip=args.ip, port=args.port)
        else:
            raise NotImplementedError(interface)


class DevShellCommandSet(OriginDevShellCommandSet):
    def do_publish(self, statement: cmd2.Statement):
        """
        Publish "dev-shell" to PyPi
        """
        # don't publish if code style wrong:
        verbose_check_call('darker', '--check')

        # don't publish if test fails:
        verbose_check_call('pytest', '-x')

        poetry_publish(
            package_root=PACKAGE_ROOT,
            version=dwload_server.__version__,
            creole_readme=False,
        )


class DevShellApp(DevShellBaseApp):
    # Remove some commands:
    delattr(cmd2.Cmd, 'do_edit')
    delattr(cmd2.Cmd, 'do_shell')
    delattr(cmd2.Cmd, 'do_run_script')
    delattr(cmd2.Cmd, 'do_run_pyscript')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intro = (
            f'Developer shell'
            f' - {bright_yellow("DWLOAD Server")}'
            f' - v{dwload_server.__version__}\n'
        )


def get_devshell_app_kwargs():
    """
    Generate the kwargs for the cmd2 App.
    (Separated because we needs the same kwargs in tests)
    """
    config = DevShellConfig(package_module=dwload_server)

    # initialize all CommandSet() with context:
    kwargs = dict(config=config)

    app_kwargs = dict(
        config=config,
        command_sets=[
            DwLoadCommandSet(**kwargs),
            DevShellCommandSet(**kwargs),
        ],
    )
    return app_kwargs


def devshell_cmdloop():
    """
    Entry point to start the "dev-shell" cmd2 app.
    Used in: [tool.poetry.scripts]
    """
    app = DevShellApp(**get_devshell_app_kwargs())
    run_cmd2_app(app)  # Run a cmd2 App as CLI or shell
