from setuptools import setup, find_packages


setup(
    name="ddns",
    version="0.0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[],
    package_data={
        '': ['*.txt'],
    },
    # metadata for upload to PyPI
    author="Radu Ciorba",
    description="DDNS",
)
