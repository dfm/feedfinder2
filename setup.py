from setuptools import setup

setup(
    name="feedfinder2",
    version="0.0.1",
    url="https://github.com/dfm/feedfinder2",
    license="MIT",
    author="Dan Foreman-Mackey",
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    description="Find the feed URLs for a website.",
    long_description=open("README.rst").read(),
    py_modules=["feedfinder2"],
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
