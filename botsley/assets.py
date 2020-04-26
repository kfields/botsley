import os
import zipfile

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))

def asset(filename):
    return os.path.join(assets_dir, filename)

def load(filename, mode='r'):
    return open(os.path.join(assets_dir, filename), mode)

def load_zip(filename):
    return zipfile.ZipFile(os.path.join(assets_dir, filename))