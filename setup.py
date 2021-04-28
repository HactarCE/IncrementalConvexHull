import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="incremental-convex-hull",
    version="1.0.1",
    description="Incremental convex hull builder and visualizer",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/HactarCE/IncrementalConvexHull",
    author="HactarCE, Manali Shirsekar, Neill Robson",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["incrementalconvexhull"],
    install_requires=["numpy", "pyglet"],
    entry_points={
        "console_scripts": [
            "visualhull=incrementalconvexhull.main:main",
        ]
    },
)
