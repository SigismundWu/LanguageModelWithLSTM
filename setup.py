# -*- coding: utf-8 -*-
from sys import version_info
from setuptools import setup, find_packages

"""This is an airflow-deploy ready version"""
REQUIRED_PACKAGES = [
    "scikit-learn",
    "scipy",
    "xlrd>=0.9.0",
    "pymysql",
    "aiohttp",
    "aiofiles",
    "bs4",
    "gensim",
    "torch",
    "xgboost"
]

if version_info.minor <= 4:  # version_info的major和minor分别取3, 4
    REQUIRED_PACKAGES.append("numpy==1.13.3")
    REQUIRED_PACKAGES.append("pandas==0.20.3")
else:
    REQUIRED_PACKAGES.append("numpy>=1.14.0, <=1.15.0")
    REQUIRED_PACKAGES.append("pandas>=0.22.0, <=0.24.0")

setup(
    name="LSTM-LanguageModel",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'LSTM-LanguageModel=LSTM-LanguageModel.cli:main'  # console_scripts指代在cli当中调用的入口名
        ]
    },
    package_data={
        '': ['*.json', '*.csv', '*.xlsx'],
    },
    install_requires=REQUIRED_PACKAGES,
    description="This is a package using LSTM-LanguageModel to evaluate the exercises' qualities",
    test_suite="tests",
    python_requires='>=3.4',
    include_package_data=True
)
