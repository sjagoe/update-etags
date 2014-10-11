from __future__ import absolute_import, print_function

import os

import yaml

from .errors import MissingConfiguration, NoSuchProject


class UpdateEtagsConfig(object):

    def __init__(self):
        self._projects = {}
        self._tags_dir = None
        self._temp_dir = None

    @classmethod
    def from_file(cls, config_path):
        if not os.path.exists(config_path):
            raise MissingConfiguration(config_path)

        with open(config_path, 'r') as fh:
            return cls.from_dict(yaml.safe_load(fh))

    @staticmethod
    def _default_tags_dir():
        return os.path.normpath(os.path.expanduser('~/.etags'))

    @staticmethod
    def _default_temp_dir():
        return os.path.normpath(os.path.expanduser('~/.etags/temp'))

    @classmethod
    def from_dict(cls, data):
        config = cls()
        for project in data.get('projects', []):
            name = project['name']
            path = project['path']
            config._projects[name] = path
        config._tags_dir = data.get('tags-dir', cls._default_tags_dir())
        config._temp_dir = data.get('temp-dir', cls._default_temp_dir())

    @property
    def projects(self):
        return list(self._projects.keys())

    @property
    def project_path(self, name):
        if name not in self._projects:
            raise NoSuchProject(name)
        return self._projects[name]

    @property
    def project_tags_path(self, name):
        if name not in self._projects:
            raise NoSuchProject(name)
        return os.path.join(self.tags_dir, name)

    @property
    def tags_dir(self):
        return self._tags_dir

    @property
    def temp_dir(self):
        return self._temp_dir

    @property
    def tags_file(self):
        return os.path.join(self.tags_dir, 'TAGS')
