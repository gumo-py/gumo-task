import setuptools


name = 'gumo-task'
version = '0.0.7'
description = 'Gumo Task Library'
dependencies = [
    f'gumo-core >= {version}',
    f'gumo-datastore >= {version}',
    'google-cloud-tasks >= 0.3.0',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    package for package in setuptools.find_packages()
    if package.startswith('gumo')
]

namespaces = ['gumo']

setuptools.setup(
    name=name,
    version=version,
    author="Gumo Project Team",
    author_email="gumo-organizer@levii.co.jp",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gumo-py/gumo",
    packages=packages,
    namespaces=namespaces,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
)
