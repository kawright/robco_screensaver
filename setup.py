"""
This module configures setuptools, which will allow us to use py2exe to
create a standalone Windows executable.
"""

from distutils.core import setup
import py2exe

setup(
    name="KrisCo Terminal Hack Screensaver",
    version="0.9.0",
    description=\
        "A screensaver in the style of Fallout's Terminal Hack minigame.",
    author="Kristoffer A. Wright",
    author_email="kris.al.wright@gmail.com",
    url="http://kriswrightdev.com/krisco_terminal_hack_screensaver",
    console=[
        "main.py"
    ],
    license="MIT",
    platforms=[
        "nt"
    ],
    include_package_data=True
)