from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from distutils.command.build import build
from distutils.command.clean import clean
import subprocess, os, sys, shutil

VERSION = '1.0.0-beta-6'
TAG = 'v' + VERSION

ROSIE_URL = "https://github.com/jamiejennings/rosie-pattern-language"
ROSIE_DIR = "rosie-pattern-language"
SRC_DIR = 'rosie'

def git_clone_rosie():
    devnull = open(os.devnull, 'w')
    cwd = os.getcwd()
    os.chdir(SRC_DIR)
    # Obtain rosie distribution
    if os.path.isdir(ROSIE_DIR):
        os.chdir(ROSIE_DIR)
        print("Found directory", os.path.join(SRC_DIR, ROSIE_DIR))
        # if not subprocess.call('git fetch origin {}'.format(TAG), shell=True, stderr=devnull):
        #     print("Unable to obtain code updates from github.  Using existing local code repository.")
    else:
        print("Rosie source code directory not found.  Attempting to clone it now...")
        subprocess.check_call(
            ('git clone -b {} --recurse-submodules {}.git {}'.format(TAG, ROSIE_URL, ROSIE_DIR)),
            shell=True)
    os.chdir(cwd)
    return
    
def build_rosie():
    cwd = os.getcwd()
    os.chdir(SRC_DIR)
    if not os.path.isdir(ROSIE_DIR):
        raise RuntimeError("Need to obtain rosie source first.  Try 'python setup.py sdist'.")
    librosie = 'librosie' + ('.dylib' if sys.platform == 'darwin' else '.so')

    print("Checking for {} and rosie.py".format(librosie))
    have_librosie = os.path.isfile(librosie)
    have_rosie_py = os.path.isfile('rosie.py')
    if have_librosie: print("Found", str(librosie))
    if have_rosie_py: print("Found", str('rosie.py'))
    if have_librosie and have_rosie_py:
        os.chdir(cwd)
        return

    os.chdir(ROSIE_DIR)
    output_dir = '..'

    # Build the Rosie shared library
    subprocess.check_call(('make', 'clean'))
    subprocess.check_call(('make', 'ROSIE_HOME="//rosie-pattern-language"', 'BREW=1'))

    # Copy built files to the right place
    subprocess.check_call(('cp',
                           'src/librosie/binaries/' + librosie,
                           output_dir + '/' + librosie))
    subprocess.check_call(('cp',
                           'src/librosie/python/rosie.py',
                           output_dir + '/rosie.py'))
    # with open(output_dir + '/rosie.py', 'w') as ROSIE_PY_FILE:
    #     subprocess.check_call(('cat',
    #                            'src/librosie/python/rosie.py',
    #                            'src/librosie/python/pypi_config.py'),
    #                           stdout = ROSIE_PY_FILE)
    os.chdir(cwd)
    return

class custom_sdist(sdist):
    def run(self):
        git_clone_rosie()
        sdist.run(self)

class custom_clean(clean):
    def run(self):
        for dir in ['build', 'dist', os.path.join(SRC_DIR, ROSIE_DIR)]:
            try:
                shutil.rmtree(dir)
            except:
                pass
        for file in ['rosie.py', 'rosie.pyc', 'librosie.so', 'librosie.dylib']:
            try:
                os.remove(os.path.join(SRC_DIR, file))
            except:
                pass
        clean.run(self)

class custom_install(install):
    def run(self):
        print("""

        The installation process will:
        (1) obtain the full rosie source code from github, if needed;
        (2) build the binary for your platform using 'make' and 'gcc/cc';
        (3) then do the python installation.

        """)
        if not os.path.isdir(os.path.join(SRC_DIR, ROSIE_DIR)): 
             git_clone_rosie()
             build_rosie()
        install.run(self)
        
class custom_build(build):
    def run(self):
        print("Building librosie...")
        git_clone_rosie()
        build_rosie()
        build.run(self)

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
            build_rosie()
except ImportError, NameError:
    class bdist_wheel():
        def run(self):
            raise RuntimeError("Package 'wheel' not installed.  Try 'pip install wheel'.")


def readme():
    readmefile = os.path.join(SRC_DIR, "README") 
    if not os.path.isfile(readmefile):
        raise RuntimeError("README file not found at " + readmefile)
    return open(readmefile).read()

setup(
    name="rosie",
    version=VERSION,

    # Do NOT set include_package_data to True, else the entire
    # rosie-pattern-language source tree will be included in the
    # binary (wheel) distribution!
    include_package_data=False,

    packages = find_packages(),

    install_requires=['cffi >= 1.9'],

    package_data = {
        '': ['librosie.*',
             'rosie/README',
             'rosie-pattern-language/VERSION',
             'rosie-pattern-language/LICENSE',
             'rosie-pattern-language/lib/*',
             'rosie-pattern-language/rpl/*',
             'rosie-pattern-language/rpl/*/*'],
    },

#    scripts = ['bin/rosie', 'bin/rosie-configure'],

    cmdclass = {
        'sdist': custom_sdist,
        'build': custom_build,
        'bdist_wheel': bdist_wheel,
        'install': custom_install,
        'clean': custom_clean,
    },

    # metadata for upload to PyPI
    author="Jamie Jennings",
    author_email="rosie.pattern.language@gmail.com",
    description="Rosie Pattern Language (replaces regex for data mining and text search)",

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
