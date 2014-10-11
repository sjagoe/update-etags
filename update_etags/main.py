from __future__ import absolute_import, print_function

import os

import click

from .config import UpdateEtagsConfig


def load_config(config_path):
    if config_path is None:
        config_path = os.path.normpath(
            os.path.expanduser('~/.update_etags.yaml'))
    return UpdateEtagsConfig.from_file(config_path)


@click.command()
@click.option('-c', '--config',
              help='The location of the update_etags config file')
def update_etags(config):
    config = load_config(config)
