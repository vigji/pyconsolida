# pyconsolida
[![tests](https://github.com/vigji/pyconsolida/actions/workflows/main.yml/badge.svg)](https://github.com/vigji/pyconsolida/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/vigji/pyconsolida/badge.svg?branch=main)](https://coveralls.io/github/vigji/pyconsolida?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Automatic data parsing to aggregate global material usage lists from construction sites budgets.

## Contents
 - The `pyconsolida` module contains utility functions to read and lint the files (for now `analisi.xlsx` with the construction site budget)
 - `scripts` contains the scripts to run for the conversions


## Installation & instructions:

Utilizzo terminale
Questi istruzioni assumono che:
1)	Si stia operando da rete icop o con VPN (per configurazione VPN guardare sotto “Primo accesso”)
2)	Si abbia un account abilitato all’accesso sul server all’indirizzo 10.0.0.7


-	Eseguire accesso con ssh al terminale:
 ```bash
  ssh nome.cognome@10.0.0.7 
  ```
-	Usando password: account icop
-	Si apre la connessione; se corretto ora vediamo all’inizio della riga:
```bash
[nome.cognome@srvgesaweb ~]$
```
-	Per eseguire lo script, digitare (in una singola linea)
```bash
cd ../../userbin/pyconsolida; source pyconsolida-env/bin/activate; python run_tabellone.py
```
(Questo comando 1) naviga fino alla location della libreria; 2) attiva l’environment di python per farla girare; 3) lancia il main script della libreria)
-	A questo punto seguire le istruzioni per l’immissione delle date di inizio e di fine tra le quali calcolare il delta. Una volta scelte le date comparirà una barra di avanzamento e lo script raccoglierà le informazioni sull’intervallo scelto.

Nota: velocità dello script. Lo script lavora in due fasi: 
 1) per ogni cantiere, processa il foglio excel di analisi e salva una versione “digerita” nella cartella cached; 
 2) raccoglie tutte le info preprocessate dalle cartelle cached. Il contenuto in cached viene ricalcolato ogni volta che:
    - si è appena aggiunta una nuova cartella dati in cui manca ancora la cartella cached;
    - si è modificato il contenuto di uno dei file della cartella dati
    - si è modificato lo script (più precisamente, il current git commit)

Siccome ricalcolare i file cached prende la maggior parte del tempo di esecuzione, quando si lavora con dei nuovi dati o si modificano vecchie cartelle è ragionevole aspettarsi un aumento dei tempi di processamento in misura proporzionale al numero di dati cambiati/aggiunti. Ogni volta che si modifica lo script bisognerà ricalcolare tutte le cache (approx. 15-30 minuti). Il tempo senza ricalcolo della cache dovrebbe essere circa 2-3 minuti


### Synch issues
Se sul server onedrive non sta sincronizzando, è possibile copiare localmente i files con (sostituire i valori con quelli giusti):

```bash
scp -r luigi.petrucco@10.0.0.7:/myshare/cantieri/exports/exported_da2023-12-01-a-2024-06-01_240829-133214 /Users/vigji/Desktop/my_copied_folder
```


### Primo accesso:

Da fuori, Installare FortiVPN per potersi collegare alla sede di Basiliano.
Lancia in esecuzione il programma.

- Configurazione con proprio username (eg luigi.petrucco)
- Una volta che la vpn sarà attiva potrai entrare nel server linux tramite programmi tipo putty o simili all'indirizzo: 10.0.0.7
- Al login stesse credenziali che hai utilizzato per la vpn.


### Developers - per il mantenimento della libreria:

Installazione programma scripts:

```bash
git clone https://github.com/vigji/pyconsolida
cd pyconsolida
python3 -m venv pyconsolida-env
source pyconsolida-env/bin/activate
pip install -e .[dev]
```
