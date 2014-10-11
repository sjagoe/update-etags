from __future__ import absolute_import, print_function


class UpdateEtagsError(Exception):
    pass


class MissingConfiguration(UpdateEtagsError):
    pass


class NoSuchProject(UpdateEtagsError):
    pass
