from setuptools import find_namespace_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    requirements_dev = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pyconsolida",
    version="0.1.0",
    description="Aggregatore dati da budget cantiere I.CO.P",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    extras_require=dict(dev=requirements_dev),
    packages=find_namespace_packages(exclude=("docs", "tests*")),
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=False,
)
