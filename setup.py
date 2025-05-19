from setuptools import setup, find_packages

setup(
    name="chiefai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "polars",
        "psycopg2-binary",
        # Add other dependencies
    ],
)