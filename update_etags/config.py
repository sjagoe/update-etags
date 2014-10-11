from __future__ import absolute_import, print_function

from itertools import chain, repeat
import os

import yaml

from .errors import MissingConfiguration


__all__ = ['UpdateEtagsConfig']


def normalize_path(path):
    return os.path.abspath(os.path.normpath(os.path.expanduser(path)))


class Project(object):

    def __init__(self, name, file_types, skip_dirs, tags_dir, temp_dir,
                 etags, etags_args, path=None):
        self._name = name
        self._file_types = file_types
        self._skip_dirs = skip_dirs
        self._tags_dir = tags_dir
        self._temp_dir = temp_dir
        self._etags = etags
        self._etags_args = etags_args
        self._path = path

    @classmethod
    def from_dict(cls, config, data, read_stdin=True):
        etags = data.get(config.ETAGS, config.etags)
        etags_args = config.etags_args + tuple(data.get(config.ETAGS_ARGS, ()))
        tags_dir = normalize_path(data.get(config.TAGS_DIR, config.tags_dir))
        temp_dir = normalize_path(data.get(config.TEMP_DIR, config.temp_dir))
        skip_dirs = config.skip_dirs + tuple(data.get(config.SKIP_DIRS, ()))

        if read_stdin and '-' not in etags_args:
            etags_args = etags_args + ('-',)

        kwargs = {}
        if 'path' in data:
            kwargs['path'] = normalize_path(data['path'])

        return cls(
            name=data['name'],
            file_types=tuple(data.get(config.FILE_TYPES, ('*',))),
            skip_dirs=skip_dirs,
            tags_dir=tags_dir,
            temp_dir=temp_dir,
            etags=etags,
            etags_args=etags_args,
            **kwargs
        )

    @property
    def name(self):
        return self._name

    @property
    def etags(self):
        return self._etags

    @property
    def etags_args(self):
        return tuple(self._etags_args)

    @property
    def tags_dir(self):
        return self._tags_dir

    @property
    def temp_dir(self):
        return self._temp_dir

    @property
    def skip_dirs(self):
        return self._skip_dirs

    @property
    def path(self):
        return self._path

    @property
    def file_types(self):
        return self._file_types

    @property
    def tags_path(self):
        return os.path.join(self.tags_dir, self._name)


class MasterProject(Project):

    @classmethod
    def from_dict(cls, config, data, projects):
        etags_args = data.get(config.ETAGS_ARGS, [])

        project_tags_files = (project.tags_path for project in projects)

        args = list(chain.from_iterable(
            zip(repeat('--include'), project_tags_files)))

        etags_args = etags_args + args
        data[config.ETAGS_ARGS] = etags_args

        return super(MasterProject, cls).from_dict(
            config, data, read_stdin=False)


class UpdateEtagsConfig(object):

    ETAGS = 'etags-command'
    ETAGS_ARGS = 'etags-args'
    FILE_TYPES = 'file-types'
    MASTER = 'master'
    PROJECTS = 'projects'
    SKIP_DIRS = 'skip-dirs'
    TAGS_DIR = 'tags-dir'
    TEMP_DIR = 'temp-dir'

    def __init__(self):
        self._projects = ()
        self._tags_dir = None
        self._temp_dir = None
        self._etags = None
        self._etags_args = None
        self._skip_dirs = ()

    @classmethod
    def from_file(cls, config_path):
        if not os.path.exists(config_path):
            raise MissingConfiguration(config_path)

        with open(config_path, 'r') as fh:
            return cls.from_dict(yaml.safe_load(fh))

    @classmethod
    def from_dict(cls, data):
        config = cls()

        config._tags_dir = tags_dir = data.get(
            cls.TAGS_DIR, cls._default_tags_dir())
        config._temp_dir = data.get(
            cls.TEMP_DIR, cls._default_temp_dir(tags_dir))
        config._etags = data.get(cls.ETAGS, cls._default_etags())
        config._etags_args = data.get(
            cls.ETAGS_ARGS, cls._default_etags_args())

        config._skip_dirs = tuple(data.get(cls.SKIP_DIRS, ()))

        projects = [
            Project.from_dict(config, project)
            for project in data.get(cls.PROJECTS, [])
        ]
        projects.append(
            MasterProject.from_dict(
                config,
                data.get(cls.MASTER, cls._default_master()),
                projects,
            ),
        )

        config._projects = tuple(projects)

        return config

    @staticmethod
    def _default_master():
        return {
            'name': 'TAGS',
        }

    @staticmethod
    def _default_tags_dir():
        return normalize_path('~/.etags')

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
    def projects(self):
        return self._projects

    @property
    def etags(self):
        return self._etags

    @property
    def etags_args(self):
        return tuple(self._etags_args)

    @property
    def tags_dir(self):
        return self._tags_dir

    @property
    def temp_dir(self):
        return self._temp_dir

    @property
    def skip_dirs(self):
        return self._skip_dirs

    def temp(self, path):
        basename = os.path.basename(path)
        return os.path.join(self.temp_dir, basename)
