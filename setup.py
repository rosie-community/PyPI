from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.sdist import sdist
import subprocess, os, sys

VERSION = '1.0.0-beta-5'
TAG = 'v' + VERSION

ROSIE_URL = "https://github.com/jamiejennings/rosie-pattern-language"
ROSIE_DIR = "rosie-pattern-language"
SRC_DIR = 'rosie'

def git_clone_rosie():
    devnull = open(os.devnull, 'w')
    if not subprocess.call(('git', 'version'), stdout=devnull) == 0:
        raise subprocess.CalledProcessError("Could not run 'git', which is required to download rosie source.")
    cwd = os.getcwd()
    os.chdir(SRC_DIR)
    # Obtain or refresh rosie distribution
    if os.path.isdir(ROSIE_DIR):
        os.chdir(ROSIE_DIR)
        subprocess.check_call(('git', 'fetch', 'origin', TAG))
    else:
        subprocess.check_call(('git', 'clone',
                               '-b', TAG,
                               '--recurse-submodules',
                               ROSIE_URL + '.git',
                               ROSIE_DIR))                
    os.chdir(cwd)
    return
    
def build_rosie():
    cwd = os.getcwd()
    os.chdir(SRC_DIR)
    if not os.path.isdir(ROSIE_DIR):
        raise RuntimeError("Need to obtain rosie source first.  Try 'python setup.py sdist'.")
    os.chdir(ROSIE_DIR)

    # Build the Rosie shared library
    subprocess.check_call(('make', 'clean'))
    subprocess.check_call(('make', 'ROSIE_HOME="//rosie-pattern-language"'))

    # Copy the built files to the top level 'rosie' dir
    if sys.platform == 'darwin':
        lib_extension = '.dylib'
    else:
        lib_extension = '.so'

    # Copy built files to the right place
    librosie = 'librosie' + lib_extension
    output_dir = '..'
    subprocess.check_call(('cp',
                           'src/librosie/binaries/' + librosie,
                           output_dir + '/' + librosie))
    with open(output_dir + '/rosie.py', 'w') as ROSIE_PY_FILE:
        subprocess.check_call(('cat',
                               'src/librosie/python/rosie.py',
                               'src/librosie/python/pypi_config.py'),
                              stdout = ROSIE_PY_FILE)
    os.chdir(cwd)
    return

class librosieInstall(install):
    def run(self):
        raise RuntimeError('Do not use setup.py install.  Use pip on the wheel file in the dist directory.')

class custom_sdist(sdist):
    def run(self):
        git_clone_rosie()
        sdist.run(self)

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
            build_rosie()
except ImportError:
    class bdist_wheel(_bdist_wheel):
        def run(self):
            raise RuntimeError("Package 'wheel' not installed.  Try 'pip install wheel'.")


def readme():
    readmefile = ROSIE_DIR + "/README" 
    if not os.path.isfile(readmefile):
        print("README file not available.  Leaving description empty.")
        return "See project README"
    return open(readmefile).read()

setup(
    name="rosie",
    version=VERSION,

    # Do NOT use include_package_data, else the entire
    # rosie-pattern-language source tree will be included in the
    # binary (wheel) distribution!
    #   include_package_data=True,

    packages = find_packages(),

    install_requires=['cffi >= 1.9'],

    package_data={
        '': ['librosie.*',
             'rosie-pattern-language/VERSION',
             'rosie-pattern-language/LICENSE',
             'rosie-pattern-language/lib/*',
             'rosie-pattern-language/rpl/*',
             'rosie-pattern-language/rpl/*/*'],
    },

    cmdclass={
        'bdist_wheel': bdist_wheel,
        'sdist': custom_sdist,
    },

    # metadata for upload to PyPI
    author="Jamie Jennings",
    author_email="rosie.pattern.language@gmail.com",
    description="Rosie Pattern Language (replaces regex for data mining and search",

    long_description=readme(),

    license="MIT",
    keywords="rosie pattern PEG regex regexp data mining text search",
    url="http://rosie-lang.org",
    project_urls={
        "Issue page": "https://github.com/jamiejennings/rosie-pattern-language/issues/",
        "Documentation": "https://github.com/jamiejennings/rosie-pattern-language/tree/master/doc/",
        "Source Code": "https://github.com/jamiejennings/rosie-pattern-language/",
    },

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: General',
        'Topic :: Utilities',
    ],

    zip_safe=False,
)
