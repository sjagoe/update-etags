import errno
import os
import sys


__all__ = ['replace']


if sys.version >= (3, 3):
    from os import replace
else:
    def _create_old_filename(filename):
        old = filename + '.old'
        index = 2
        while os.path.exists(old):
            old = filename + '-%s.old' % index
            index += 1
        return old

    def replace(src, dst):
        try:
            os.rename(src, dst)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            old = _create_old_filename(dst)
            os.rename(dst, old)
            os.rename(src, dst)
            os.unlink(old)
