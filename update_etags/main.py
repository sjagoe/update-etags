from __future__ import absolute_import, print_function

import logging
import os

import click

from .config import UpdateEtagsConfig
from .update_etags import UpdateEtags

logger = logging.getLogger(__name__)


def load_config(config_path):
    if config_path is None:
        config_path = os.path.normpath(
            os.path.expanduser('~/.update-etags.yaml'))
    return UpdateEtagsConfig.from_file(config_path)


@click.command()
@click.option('-c', '--config',
              help='The location of the update_etags config file')
@click.option('-d', '--debug', is_flag=True, default=False,
              help='Enable debugging output')
def update_etags(config, debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)-8.8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.info('Starting update_etags')
    config = load_config(config)
    etags = UpdateEtags(config)
    etags.update_all_tags()
