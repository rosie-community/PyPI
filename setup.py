from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from distutils.command.build import build
from distutils.command.clean import clean
import subprocess, os, sys, shutil

VERSION = '1.0.0-beta-10'
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
        os.chdir(ROSIE_DIR)
    # Copy rosie.py out of the rosie source code to the top level
    output_dir = '..'
    subprocess.check_call(('cp',
                           'src/librosie/python/rosie.py',
                           output_dir + '/rosie.py'))
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
                           'src/librosie/binaries/rosie',
                           output_dir + '/rosie_cli'))
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
except:
    class bdist_wheel():
        def run(self):
            raise RuntimeError("Package 'wheel' not installed.  Try 'pip install wheel'.")


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
             'rosie_cli',
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

    long_description="""
Rosie and the Rosie Pattern Language (RPL)

RPL expressions are patterns for matching text, similar to regex but
more powerful.  You can use RPL for text pattern matching the way you
might use PCRE or regex in Perl, Python, or Java.  Unlike regex, RPL
is readable and maintainable, and packages of rpl are easily shared.

The Rosie project provides a library so you can use RPL from a variety
of programming languages.  We also provide an interactive read-eval-
print loop for pattern development and debugging, and an RPL compiler.
The Rosie matching engine is very small and reasonably fast.

Rosie's home page:
  http://rosie-lang.org

The repository of record for the Rosie project is located at:
  https://github.com/jamiejennings/rosie-pattern-language

Open issues are at:
  https://github.com/jamiejennings/rosie-pattern-language/issues

Before opening an issue with a bug report or an enhancement request,
please check the current open issues.
""",

    license="MIT",
    keywords="rosie pattern language PEG regex regexp data mining text search",
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
