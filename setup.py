#!/usr/bin/env python
from setuptools import setup

install_requires = open("requirements.txt").read().strip().split("\n")
dev_requires = open("dev-requirements.txt").read().strip().split("\n")
extras = {"dev": dev_requires}

setup(
    name="target-google-ads",
    version="1.0.3",
    description="Singer.io target for writing data to Google Ads API",
    author="lideke",
    url="https://github.com/DTSL/target-google-ads",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    packages=["target_google_ads"],
    install_requires=install_requires,
    extras_require=extras,
    entry_points="""
          [console_scripts]
          target-google-ads=target_google_ads:main
      """
)
