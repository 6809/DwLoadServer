from pathlib import Path

import cmd2
from dev_shell.base_cmd2_app import DevShellBaseApp, run_cmd2_app
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.config import DevShellConfig
from dev_shell.utils.colorful import bright_yellow
from dev_shell.utils.subprocess_utils import verbose_check_call
from poetry_publish.publish import poetry_publish

import dwload_server


PACKAGE_ROOT = Path(dwload_server.__file__).parent.parent.parent


@cmd2.with_default_category('DWLOAD Server Commands')
class DwLoadCommandSet(DevShellBaseCommandSet):
    pass  # TODO


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
            creole_readme=True,  # don't publish if README.rst is not up-to-date
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
            f'Developer shell - {bright_yellow("DWLOAD Server")} - v{dwload_server.__version__}\n'
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
