# NYC Taxi Mini-EDA

One-shot exploratory analysis of **100 k Yellow Taxi trips (Jan 2019)**  
using *Pandas 2.2* and *Python 3.12*.

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
python src/clean.py --src data/raw/yellow_tripdata_2019-01.csv
```

Or simply **open notebooks/eda.ipynb** and *Run All* (≈60 s).