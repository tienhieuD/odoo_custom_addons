from . import models


def _uninstall_hook(env):
    env['create.view.split.wizard'].remove_split_view_from_action_window()
