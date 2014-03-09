from setuptools import Command, find_packages, setup


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
    version='0.1.0',
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
        'injector',
        'argh',
    ],
    cmdclass={'test': PyTest},
    )
