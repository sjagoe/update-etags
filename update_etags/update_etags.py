from __future__ import absolute_import, print_function

import fnmatch
import logging
import os
import subprocess

from ._compat import replace

logger = logging.getLogger(__name__)


def _any_match(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def _generate_files_to_tag(path, types, skip_dirs):
    for dirpath, dirnames, filenames in os.walk(path):
        new_dirnames = [name for name in dirnames
                        if not _any_match(name, skip_dirs)]
        dirnames[:] = new_dirnames
        for filename in filenames:
            if _any_match(filename, types):
                yield os.path.join(dirpath, filename)


class UpdateEtags(object):

    def __init__(self, config):
        self._config = config

    def _run_etags(self, etags_cmd, tags_dst, temp_tags,
                   filename_generator=None):
        stdout = open(temp_tags, 'wb')
        try:
            logger.debug('Running command {!r}'.format(etags_cmd))
            etags = subprocess.Popen(
                etags_cmd, stdout=stdout, stdin=subprocess.PIPE)
            if filename_generator is not None:
                for filename in filename_generator:
                    fname = u'{}\n'.format(filename).encode('utf-8')
                    etags.stdin.write(fname)
            etags.stdin.close()
            etags.communicate()
        except Exception:
            logger.exception('Error occurred running tag-generator')
            if etags.poll() is None:
                etags.terminate()
                etags.communicate()
            if os.path.exists(temp_tags):
                os.unlink(temp_tags)
            stdout.close()
            raise
        else:
            stdout.close()
            replace(temp_tags, tags_dst)

    def _update_tags_for_project(self, project):
        if project.path is not None:
            filename_generator = _generate_files_to_tag(
                project.path, project.file_types, project.skip_dirs)
        else:
            filename_generator = None

        tags_dst = project.tags_path

        temp_tags = self._config.temp(tags_dst)

        if not os.path.exists(project.tags_dir):
            logger.debug('Creating tags dir {}'.format(project.tags_dir))
            os.makedirs(project.tags_dir)
        if not os.path.exists(project.temp_dir):
            logger.debug('Creating temp dir {}'.format(project.temp_dir))
            os.makedirs(project.temp_dir)

        self._run_etags(project.etags_command(), tags_dst, temp_tags,
                        filename_generator)

    def update_all_tags(self):
        for project in self._config.projects:
            logger.info('Updating project {}'.format(project.name))
            self._update_tags_for_project(project)
