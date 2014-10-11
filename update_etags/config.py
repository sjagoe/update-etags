from __future__ import absolute_import, print_function

import os

import yaml

from .errors import MissingConfiguration, NoSuchProject


class UpdateEtagsConfig(object):

    def __init__(self):
        self._projects = {}
        self._tags_dir = None
        self._temp_dir = None
        self._etags = None
        self._etags_args = None

    @classmethod
    def from_file(cls, config_path):
        if not os.path.exists(config_path):
            raise MissingConfiguration(config_path)

        with open(config_path, 'r') as fh:
            return cls.from_dict(yaml.safe_load(fh))

    @classmethod
    def from_dict(cls, data):
        config = cls()

        config._projects = {
            project['name']: {
                'path': project['path'],
                'file-types': project.get('file-types', '*'),
            }
            for project in data.get('projects', [])
        }

        config._tags_dir = tags_dir = data.get(
            'tags-dir', cls._default_tags_dir())
        config._temp_dir = data.get(
            'temp-dir', cls._default_temp_dir(tags_dir))
        config._etags = data.get('etags-command', cls._default_etags())
        config._etags_args = data.get('etags-args', cls._default_etags_args())

        return config

    @staticmethod
    def _default_tags_dir():
        return os.path.normpath(os.path.expanduser('~/.etags'))

    @staticmethod
    def _default_etags():
        return 'etags'

    @staticmethod
    def _default_etags_args():
        return ()

    @staticmethod
    def _default_temp_dir(tags_dir):
        return os.path.join(tags_dir, 'temp')

    @property
    def etags(self):
        return self._etags

    @property
    def etags_args(self):
        return tuple(self._etags_args)

    @property
    def projects(self):
        return list(self._projects.keys())

    @property
    def tags_dir(self):
        return self._tags_dir

    @property
    def temp_dir(self):
        return self._temp_dir

    @property
    def tags_file(self):
        return os.path.join(self.tags_dir, 'TAGS')

    def project_path(self, name):
        if name not in self._projects:
            raise NoSuchProject(name)
        return self._projects[name]['path']

    def project_file_types(self, name):
        if name not in self._projects:
            raise NoSuchProject(name)
        return self._projects[name]['file-types']

    def project_tags_path(self, name):
        if name not in self._projects:
            raise NoSuchProject(name)
        return os.path.join(self.tags_dir, name)

    def temp(self, path):
        basename = os.path.basename(path)
        return os.path.join(self.temp_dir, basename)
