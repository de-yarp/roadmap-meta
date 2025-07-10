import pandas as pd
import matplotlib.pyplot as plt
import logging
import click

from pathlib import Path
from dataclasses import dataclass
from typing import Tuple


# ---------- 1. параметры ----------------
@dataclass
class Config:
    src: Path
    out_dir: Path = Path("data/processed")
    plot_dir: Path = Path("plots")
    clean_path: Path = out_dir / "taxi_clean.parquet"
    sample_rows: int = 100000
    log_path: Path = Path("logs/pipe.log")


# ---------- 2. helpers ------------------
def load_sample(cfg: Config) -> pd.DataFrame:
    return pd.read_csv(cfg.src, nrows=cfg.sample_rows)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # index
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    # type
    cols_to_cat = [
        "VendorID",
        "RatecodeID",
        "store_and_fwd_flag",
        "PULocationID",
        "DOLocationID",
        "payment_type",
        "passenger_count",
    ]  # ---columns to change type of to category
    df[cols_to_cat] = df[cols_to_cat].astype("category")
    # cleaning (separating real data)
    df = df[
        (df["trip_distance"] > 0)
        & (df["passenger_count"] != 0)
        & (df["fare_amount"] > 0)
        & (df["tpep_pickup_datetime"] >= "2019-01-01")
    ]
    # adding new informative columns
    df["trip_duration_min"] = (
        df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    ).dt.total_seconds() / 60
    df["tip_percent"] = (df.tip_amount / df.fare_amount) * 100
    # changed order to a more logical
    column_order = [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "trip_duration_min",
        "passenger_count",
        "trip_distance",
        "RatecodeID",
        "store_and_fwd_flag",
        "PULocationID",
        "DOLocationID",
        "payment_type",
        "fare_amount",
        "extra",
        "mta_tax",
        "tip_amount",
        "tip_percent",
        "tolls_amount",
        "improvement_surcharge",
        "total_amount",
        "congestion_surcharge",
    ]
    df = df[column_order]
    # deleting impossible rides by duration
    df = df[df["trip_duration_min"] < 186]
    return df


def aggregate(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # aggregate and sort
    revenue = pd.DataFrame(df.groupby(by="PULocationID").total_amount.sum())
    revenue = revenue.sort_values(by="total_amount", ascending=False)
    revenue = revenue.rename(columns={"total_amount": "Total Amount"})

    by_hour = (
        df.set_index("tpep_pickup_datetime")[["total_amount"]]
        .resample("H")
        .mean(numeric_only=True)
    )
    by_hour = by_hour.rename_axis("Hour", axis=0)
    by_hour.index = by_hour.index.hour
    by_hour = by_hour.rename(columns={"total_amount": "Total Amount"})

    return revenue, by_hour


def save_aggregated(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    revenue, by_hour = aggregate(df)
    revenue.to_parquet(out_dir / "revenue_by_loc.parquet", index=True)
    by_hour.to_parquet(out_dir / "check_by_hour.parquet", index=True)


def make_plots(df: pd.DataFrame, plot_dir: Path) -> None:
    # check
    plot_dir.mkdir(parents=True, exist_ok=True)
    revenue, by_hour = aggregate(df)

    # bar top 10 revenue
    revenue = revenue["Total Amount"].nlargest(10)
    revenue.plot(kind="bar")
    plt.title("Top 10 locations by revenue")
    plt.savefig(plot_dir / "revenue_top10.png", dpi=300, bbox_inches="tight")
    plt.clf()

    # line check by hour
    by_hour.plot(kind="line", marker="o")
    plt.title("Average revenue per hour")
    plt.savefig(plot_dir / "check_by_hour.png", dpi=300, bbox_inches="tight")
    plt.clf()

    # box trip distribution
    df.boxplot(column="trip_duration_min")
    plt.title("Trip Duration Distribution(< 186 min)")
    plt.savefig(plot_dir / "duration_distribution.png", dpi=300, bbox_inches="tight")
    plt.clf()


def run(cfg: Config) -> None:
    logging.basicConfig(
        filename=cfg.log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    logging.info("Start pipeline, file=%s, sample=%s", cfg.src, cfg.sample_rows)
    raw_data = load_sample(cfg)
    logging.info("Loaded rows: %s", len(raw_data))

    df_clean = clean(raw_data)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(cfg.clean_path, index=False)
    logging.info("Saved clean parquet: %s, rows=%s", cfg.clean_path, len(df_clean))

    save_aggregated(df_clean, cfg.out_dir)
    make_plots(df_clean, cfg.plot_dir)
    logging.info("Pipeline finished OK")


# ---------- 4. CLI ----------------------
@click.command()
@click.option(
    "--src", type=click.Path(exists=True), required=True, help="Path to raw CSV file"
)
@click.option(
    "--sample", default=100_000, show_default=True, help="Number of rows to load"
)
def cli(src, sample):
    cfg = Config(src=Path(src), sample_rows=sample)
    run(cfg)


if __name__ == "__main__":
    cli()
