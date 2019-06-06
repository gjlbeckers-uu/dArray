import sys
import versioneer
import setuptools

if sys.version_info < (3,6):
    print("Darr requires Python 3.6 or higher please upgrade")
    sys.exit(1)

long_description = \
"""
Darr is a Python science library that enables you to work with potentially
very large disk-based numeric arrays, and share this data with others who do
not use Darr, or even Python, without exporting anything or requiring much
explanation. It is also an easy way of make sure you can read your own data
when using different tools, perhaps in the future. Tool-independance of data
is in line with good scientific practice as it promotes wide and long-term
accessibility. More rationale for this approach is provided
`here <https://darr.readthedocs.io/en/latest/rationale.html>`__.

Darr supports efficient read/write/append access. Data is disk-persistent
and memory mapped. It is based on universally readable flat binary
files and automatically generated text files with human-readable explanation
of precisely how your binary data is stored, as well as examples code for
reading the specific data in a variety of current scientific data tools
such as Python, R, Julia, IDL, Matlab, Maple, and Mathematica (see
`example array <https://github.com/gbeckers/Darr/tree/master/examplearrays/examplearray_uint64.darr>`__).

Darr currently supports numerical N-dimensional arrays, and experimentally
supports numerical ragged arrays, i.e. a series of arrays in which one
dimension varies in length.

See this `tutorial <https://darr.readthedocs.io/en/latest/tutorial.html>`__
for a brief introduction, or the
`documentation <http://darr.readthedocs.io/>`__ for more info.

Darr is currently pre-1.0, still undergoing significant development. It is
open source and freely available under the `New BSD License
<https://opensource.org/licenses/BSD-3-Clause>`__ terms.


Features
--------

-   Purely based on **flat binary** and **text** files, tool independence.
-   Supports **very large data arrays** through **memory-mapped** file access.
-   Data read/write access through **NumPy indexing**
-   Data is easily **appendable**.
-   **Human-readable explanation of how the binary data is stored** is saved 
    in a README text file.
-   README also contains **examples of how to read the array** in popular 
    analysis environments such as Python (without Darr), R, Julia, 
    Octave/Matlab, GDL/IDL, Maple, and Mathematica.
-   **Many numeric types** are supported: (u)int8-(u)int64, float16-float64, 
    complex64, complex128.
-   Easy use of **metadata**, stored in a separate JSON text file.
-   **Minimal dependencies**, only NumPy.
-   **Integrates easily** with the Dask or NumExpr libraries for 
    **numeric computation on very large Darr arrays**.

See the [documentation](http://darr.readthedocs.io/) for more information.

"""

setuptools.setup(
    name='darr',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=['darr', 'darr.tests'],
    url='https://github.com/gbeckers/darr',
    license='BSD-3',
    author='Gabriel J.L. Beckers',
    author_email='gabriel@gbeckers.nl',
    description='Memory-mapped numeric arrays, based on a '\
                'format that is self-explanatory and tool-independent',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires='>=3.6',
    install_requires=['numpy'],
    data_files = [("", ["LICENSE"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
    ],
    project_urls={  # Optional
        'Source': 'https://github.com/gbeckers/darr',
    },
)
