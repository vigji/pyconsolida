# pyconsolida
[![tests](https://github.com/vigji/pyconsolida/actions/workflows/main.yml/badge.svg)](https://github.com/vigji/pyconsolida/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/vigji/pyconsolida/badge.svg?branch=main)](https://coveralls.io/github/vigji/pyconsolida?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
Aggregatore dati da budget cantiere I.CO.P.

## Organizzazione
 - Il modulo `pyconsolida` contiene utility functions per leggere e aggiustare file, per ora analisi.xlsx con budget di cantiere;
 - La cartella `scripts` contiene gli script da eseguire per effettuare conversioni.


## Installazione
Per installare ed eseguire, lonare la repo con 
```
git clone https://github.com/vigji/pyconsolida
```
Navigare da terminale fino alla repo e installare: 
```bash
cd pyconsolida
pip install -e .
```
Per runnare scripts, 
```bash
cd scripts
python nome_script.py
```
