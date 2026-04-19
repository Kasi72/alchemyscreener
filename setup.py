from setuptools import setup, find_packages

setup(
    name='alchemyscreener',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
        'pandas',  # Example dependency
        'numpy',   # Example dependency
    ],
    author='Kasi72',
    author_email='your_email@example.com',
    description='A package for screening data using algorithms.',
    url='https://github.com/Kasi72/alchemyscreener',
)