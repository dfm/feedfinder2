import os
import sys
from setuptools import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

setup(
    name="txfeedfinder2",
    version="0.0.2b2",
    url="https://github.com/scrunchenterprises/txfeedfinder2",
    license="MIT",
    author="David P. Novakovic",
    author_email="david@scrunch.com",
    install_requires=[
        "treq",
        "beautifulsoup4",
    ],
    description="Find the feed URLs for a website.",
    long_description=open("README.rst").read(),
    py_modules=["txfeedfinder2"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
