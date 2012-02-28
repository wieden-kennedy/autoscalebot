#/usr/bin/env python
import os
from setuptools import setup, find_packages
from heroku_web_autoscale import version

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

setup(
    name="heroku-web-autoscale",
    description="Automatic scaling of web dynos on Heroku",
    author="Steven Skoczen",
    author_email="steven.skoczen@wk.com",
    url="https://github.com/wieden-kennedy/heroku-web-autoscale",
    version=version,
    install_requires=["heroku"],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': ['heroku_web_autoscaler = heroku_web_autoscale.cli:main'],
    },
)
