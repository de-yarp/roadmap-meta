# NYC Taxi Mini-EDA

One-shot exploratory analysis of **100 k Yellow Taxi trips (Jan 2019)**  
built with **Python 3.12 + Pandas 2.2**.  
Outputs: cleaned Parquet, two aggregate tables, three exploratory charts.

[![pipeline](https://img.shields.io/badge/pipeline-passing-brightgreen)](logs/pipe.log)

## Project layout

```text
data/
    raw/            # original CSV sample
    processed/      # cleaned Parquet + aggregates
plots/              # png charts
src/                # pipeline code
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to reproduce

```bash
make data                                                                       # ---download the raw .csv dataset
python src/pipe.py --src data/raw/yellow_tripdata_2019-01.csv --sample 100000   # ---run the pipeline
```