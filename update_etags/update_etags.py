from __future__ import absolute_import, print_function

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

    def update_tags_for_project(self, project):
        project_path = self._config.project_path(project)
        project_file_types = self._config.project_file_types(project)

        filename_generator = _generate_files_to_tag(
            project_path, project_file_types)

        tags_dst = self._config.project_tags_path(project)
        temp_tags = self._config.temp(tags_dst)
        etags_cmd = [self._config.etags, '-o', temp_tags, '-']

        try:
            etags = subprocess.Popen(etags_cmd, stdin=subprocess.PIPE)
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

    def update_all_tags(self):
        for project in self._config.projects:
            self.update_tags_for_project(project)
