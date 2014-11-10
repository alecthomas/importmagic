import sys
from setuptools import Command, find_packages, setup

sys.path.insert(0, '.')
import importmagic

version = importmagic.__version__


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='importmagic',
    url='http://github.com/alecthomas/importmagic',
    download_url='http://pypi.python.org/pypi/importmagic',
    version=version,
    options=dict(egg_info=dict(tag_build='')),
    description='Python Import Magic - automagically add, remove and manage imports',
    long_description='See http://github.com/alecthomas/importmagic for details.',
    license='BSD',
    platforms=['any'],
    packages=find_packages(),
    author='Alec Thomas',
    author_email='alec@swapoff.org',
    install_requires=[
        'setuptools >= 0.6b1',
    ],
    cmdclass={'test': PyTest},
)
