import os
#
import zipfile

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))
#data_dir = 'data'

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def load(filename, mode='r'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

def load_zip(filename):
    return zipfile.ZipFile(os.path.join(data_dir, filename))