from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    requirements_dev = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pyconsolida",
    version="1.0.3",
    description="Aggregatore dati da budget cantiere I.CO.P",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "numba>=0.53.0",
        "openpyxl>=3.0.0",
        "tqdm",
        "xlrd",
        "GitPython",
        "pyarrow",
        "tabulate",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    extras_require=dict(dev=requirements_dev),
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/vigji/pyconsolida",
    author="Luigi Petrucco",
    author_email="luigi.petrucco@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    zip_safe=False,
)
