import os

from setuptools import setup, find_packages

from botsley_setup.install import install
from botsley_setup.develop import develop

with open("README.md", "r") as fh:
    long_description = fh.read()
    
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

datadir = 'share/botsley'
data_files = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]

packages = find_packages(exclude=["__botsley__", "tests"])

setup(
    name='botsley',
    packages=packages,
    include_package_data=True,
    data_files=data_files,
    use_scm_version = {
        "local_scheme": "no-local-version",
        'write_to': 'botsley/version.py',
        'write_to_template': 'version = "{version}"',
        'tag_regex': r'^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$'
    },
    setup_requires=['setuptools_scm'],
    cmdclass={
        'install': install,
        'develop': develop
    },
    install_requires=requirements,
    entry_points={"console_scripts": ["botsley = botsley.command:cli"]},
    author="Kurtis Fields",
    author_email="kurtisfields@gmail.com",
    description="Asynchronous Behavior System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/botsley/botsley",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.5',
)