from __future__ import absolute_import, print_function

from itertools import chain, repeat
import fnmatch
import os
import subprocess

from ._compat import replace


def _generate_files_to_tag(path, types):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if any(fnmatch.fnmatch(filename, pattern) for pattern in types):
                yield os.path.join(dirpath, filename)


class UpdateEtags(object):

    def __init__(self, config):
        self._config = config

    def _run_etags(self, etags_cmd, tags_dst, temp_tags,
                   filename_generator=None):
        try:
            etags = subprocess.Popen(etags_cmd, stdin=subprocess.PIPE)
            if filename_generator is not None:
                for filename in filename_generator:
                    etags.stdin.write('{}\n'.format(filename))
            etags.stdin.close()
            etags.wait()
        except Exception:
            if etags.poll() is None:
                etags.terminate()
                etags.communicate()
            if os.path.exists(temp_tags):
                os.unlink(temp_tags)
            raise
        else:
            replace(temp_tags, tags_dst)

    def _update_tags_for_project(self, project):
        project_path = self._config.project_path(project)
        project_file_types = self._config.project_file_types(project)

        filename_generator = _generate_files_to_tag(
            project_path, project_file_types)

        tags_dst = self._config.project_tags_path(project)
        temp_tags = self._config.temp(tags_dst)
        etags_cmd = [self._config.etags, '-o', temp_tags, '-']

        self._run_etags(etags_cmd, tags_dst, temp_tags, filename_generator)

    def _generate_master_tags_file(self):
        master_tags_file = self._config.tags_file
        tags_temp = self._config.temp(master_tags_file)
        project_tags_files = [self._config.project_tags_path(project)
                              for project in self._config.projects]

        args = list(chain.from_iterable(
            zip(repeat('--include'), project_tags_files)))

        etags_cmd = [self._config.etags, '-o', tags_temp] + args

        self._run_etags(etags_cmd, master_tags_file, tags_temp)

    def update_all_tags(self):
        for project in self._config.projects:
            self._update_tags_for_project(project)
        self._generate_master_tags_file()
