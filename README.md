# pyconsolida
[![tests](https://github.com/vigji/pyconsolida/actions/workflows/main.yml/badge.svg)](https://github.com/vigji/pyconsolida/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/vigji/pyconsolida/badge.svg?branch=main)](https://coveralls.io/github/vigji/pyconsolida?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Automatic data parsing from construction sites budgets to raw material usage lists

## Contents
 - The `pyconsolida` module contains utility functions to read and lint the files (for now `analisi.xlsx` with the construction site budget)
 - `scripts` contains the scripts to run for the conversions


## Installation & instructions:
To install, first clone the repo
```
git clone https://github.com/vigji/pyconsolida
```
Browse from terminal to the folder and type:
```bash
cd pyconsolida
pip install -e .
```
To run the scripts:
```bash
cd scripts
python ....py
```
