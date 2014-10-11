import os
import unittest

import yaml

from ..config import Project, MasterProject, UpdateEtagsConfig, normalize_path


TEST_CONFIG = """\
tags-dir: ~/.tags
temp-dir: ~/.tags/tmp
etags-command: ctags
etags-args: ["arg1", "arg2"]
skip-dirs:
  - ".*"
  - "__pycache__"
  - "*.egg-info"

master:
  name: TAGS
  etags-args: ["arg3"]

projects:
  - name: project_a
    path: /home/simon/workspace/project_a
    etags-command: etags
    file-types:
      - "*.py"
    skip-dirs:
      - "skip"
  - name: project_b
    path: /home/simon/workspace/project_b
    etags-args: ["arg3", "arg4"]
    file-types:
      - "*.py"
      - "*.c"

"""


class TestConfig(unittest.TestCase):

    def test_from_dict(self):
        # Given
        data = yaml.safe_load(TEST_CONFIG)

        # When
        config = UpdateEtagsConfig.from_dict(data)

        # Then
        self.assertEqual(len(config.projects), 3)
        project_a, project_b, master = config.projects

        self.assertEqual(project_a.name, 'project_a')
        self.assertEqual(project_a.etags, 'etags')
        self.assertEqual(project_a.etags_args, ('arg1', 'arg2', '-'))
        self.assertEqual(project_a.file_types, ('*.py',))
        self.assertEqual(
            project_a.skip_dirs, ('.*', '__pycache__', '*.egg-info', 'skip'))
        self.assertEqual(
            project_a.tags_path, normalize_path(
                os.path.join(project_a.tags_dir, project_a.name)))
        self.assertIsInstance(project_a, Project)

        self.assertEqual(project_b.name, 'project_b')
        self.assertEqual(project_b.etags, 'ctags')
        self.assertEqual(
            project_b.etags_args, ('arg1', 'arg2', 'arg3', 'arg4', '-'))
        self.assertEqual(project_b.file_types, ('*.py', '*.c',))
        self.assertEqual(
            project_b.skip_dirs, ('.*', '__pycache__', '*.egg-info'))
        self.assertIsInstance(project_b, Project)

        self.assertEqual(master.name, 'TAGS')
        self.assertEqual(master.etags, 'ctags')
        self.assertEqual(
            master.etags_args,
            (
                'arg1', 'arg2', 'arg3',
                '--include', project_a.tags_path,
                '--include', project_b.tags_path,
            ),
        )
        self.assertIsInstance(master, MasterProject)
