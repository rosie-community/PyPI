## PyPI

Python package for Rosie Pattern Language, to enable `pip install rosie`

## Overview

This repository contains everything needed to generate a python
package that can be installed using pip, EXCEPT for the Rosie source
code.

When you run 'python setup.py sdist', which generates a source
distribution, the Rosie source will be cloned from github.  The
version obtained is specified by the VERSION variable at the top of
setup.py.

Generating the source distribution must be done before the wheel can
be created, because the Rosie source is needed to produce the wheel.

## Instructions

(1) Build the source distribution

    The 'sdist' command obtains the rosie source from github and creates a
    source distribution.

(2) Build the wheel

    The 'bdist_wheel' command builds rosie and creates a binary (wheel)
    distribution that can be installed with pip.

## Example

Here's how I generate and install the wheel on my OS X machine:

``` 
python setup.py sdist
python setup.py bdist_wheel
pip install dist/rosie-1.0.0b5-cp27-cp27m-macosx_10_13_intel.whl
```

And then the upload:

```
twine upload dist/*
```



