from setuptools import setup, find_packages

setup(
    name="mtb",
    version="0.1.0",
    description="A toolbox for application support teams with file watching, purging, backup and more.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyyaml",
        "python-json-logger",
        "watchdog",  # for file watching functionality
    ],
    entry_points={
        "console_scripts": [
            "mtb = mtb.mtb:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
