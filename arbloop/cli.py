# -*- coding: utf-8 -*-
import importlib
import os
import pkgutil

import click


class MultiCli(click.MultiCommand):
    plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

    def list_commands(self, ctx):
        modules = pkgutil.iter_modules([self.plugin_folder])
        return [name for _, name, _ in modules]

    def get_command(self, ctx, name):
        if name not in self.list_commands(ctx):
            return None
        return importlib.import_module('arbloop.commands.' + name).cli


cli = MultiCli()

if __name__ == '__main__':
    cli()
