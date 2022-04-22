#!/usr/bin/env python

from setuptools import setup

setup(
    name="target-google-ads",
    version="0.0.1",
    description="Singer.io target for writing data to Google Ads API",
    author="lideke",
    url="https://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_google_ads"],
    install_requires=[
        "singer-python==5.12.2",
        "requests==2.26.0",
        "backoff==1.8.0",
        "google-ads==15.0.0",
        "protobuf==3.17.3",
    ],
    extras_require={
        "dev": [
            "pylint",
        ]
    },
    entry_points="""
          [console_scripts]
          target-google-ads=target_google_ads:main
      """,
    packages=["tap_google_ads"],
)
