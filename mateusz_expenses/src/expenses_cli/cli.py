from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import typer
from typing import Annotated

app = typer.Typer(no_args_is_help=True)


def read_file(file_name: str = "data/transactions.csv") -> pd.DataFrame:
    return pd.read_csv(file_name, sep=";").dropna(subset=["categoryName"])


def uah_to_pln_outcome(row: pd.Series, rate: float) -> pd.Series:
    row["outcome"] = round(row["outcome"] / rate, 2)
    row["outcomeCurrencyShortTitle"] = "PLN"
    return row


def aggregate_outcome(
    df: pd.DataFrame, date_from: str, date_to: str, uah_rate: float
) -> pd.DataFrame:
    cols = ["categoryName", "outcome", "outcomeCurrencyShortTitle"]
    mask_period = (df["date"] >= date_from) & (df["date"] < date_to)
    expenses = df[(df["income"] == 0) & mask_period][cols]
    mask = expenses["outcomeCurrencyShortTitle"] == "UAH"
    expenses.loc[mask] = expenses.loc[mask].apply(
        uah_to_pln_outcome, axis=1, rate=uah_rate
    )
    expenses = expenses.groupby(
        by=["categoryName", "outcomeCurrencyShortTitle"], as_index=False
    ).sum()
    return expenses


def uah_to_pln_income(row: pd.Series, rate: float) -> pd.Series:
    row["income"] = round(row["income"] / rate, 2)
    row["incomeCurrencyShortTitle"] = "PLN"
    return row


def aggregate_income(
    df: pd.DataFrame, date_from: str, date_to: str, uah_rate: float
) -> pd.DataFrame:
    cols = ["categoryName", "income", "incomeCurrencyShortTitle"]
    mask_period = (df["date"] >= date_from) & (df["date"] < date_to)
    income = df[(df["outcome"] == 0) & mask_period][cols]
    mask = income["incomeCurrencyShortTitle"] == "UAH"
    income.loc[mask] = income.loc[mask].apply(uah_to_pln_income, axis=1, rate=uah_rate)
    income = income.groupby(
        by=["categoryName", "incomeCurrencyShortTitle"], as_index=False
    ).sum()
    return income


def strip_currency_inplace_txt(
    df_o: pd.DataFrame,
    df_i: pd.DataFrame,
    out_path: str = "logs/non_pln_outcome.txt",
    inc_path: str = "logs/non_pln_income.txt",
) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(inc_path).parent.mkdir(parents=True, exist_ok=True)

    mask_o = df_o["outcomeCurrencyShortTitle"] != "PLN"
    mask_i = df_i["incomeCurrencyShortTitle"] != "PLN"

    # запись читаемым форматом
    with open(out_path, "w", encoding="utf-8") as f:
        for row in df_o.loc[mask_o].itertuples(index=False):
            f.write(" | ".join(map(str, row)) + "\n")

    with open(inc_path, "w", encoding="utf-8") as f:
        for row in df_i.loc[mask_i].itertuples(index=False):
            f.write(" | ".join(map(str, row)) + "\n")

    # зачистка inplace
    df_o.drop(index=df_o.index[mask_o], inplace=True)
    df_o.drop(labels="outcomeCurrencyShortTitle", axis=1, inplace=True)
    df_i.drop(index=df_i.index[mask_i], inplace=True)
    df_i.drop(labels="incomeCurrencyShortTitle", axis=1, inplace=True)

    df_o.sort_values(by="outcome", inplace=True, ascending=False)
    df_i.sort_values(by="income", inplace=True, ascending=False)

    df_o.reset_index(drop=True, inplace=True)
    df_i.reset_index(drop=True, inplace=True)


def make_pie(df_o: pd.DataFrame, df_i: pd.DataFrame) -> None:

    # ----------OUTCOME----------
    values = df_o["outcome"].to_numpy()
    labels = df_o["categoryName"].to_numpy()

    fig, ax = plt.subplots(figsize=(16, 9))  # крупнее холст
    min_pct = 1  # не показывать проценты для сегментов <1%

    def fmt(p):
        return f"{p:.1f}%" if p >= min_pct else ""

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,  # названия в легенде, не вокруг круга
        autopct=fmt,  # проценты внутри
        pctdistance=0.77,  # ближе к центру
        startangle=90,
        # wedgeprops=dict(width=0.4, edgecolor="white", linewidth=1),  # пончик
        wedgeprops=dict(edgecolor="white", linewidth=0.8),
        textprops=dict(fontsize=11),
    )
    # Сдвигаем область осей влево
    ax.set_position([0.5, 0.1, 0.6, 0.8])
    # [left, bottom, width, height] — доли от размеров фигуры
    ax.set(aspect="equal")

    # Легенда справа: Название: сумма (и доля)
    total = values.sum()
    legend_labels = [
        f"{n}: {v:.2f} ({v/total*100:.1f}%)" for n, v in zip(labels, values)
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Категории",
        loc="center left",
        bbox_to_anchor=(1, 0.5),  # вынести за пределы графика
        frameon=False,
        fontsize=11,
        title_fontsize=12,
    )

    plt.savefig("plots/expenses.png", dpi=600, bbox_inches="tight")
    plt.close()

    # ----------INCOME----------
    values = df_i["income"].to_numpy()
    labels = df_i["categoryName"].to_numpy()

    fig, ax = plt.subplots(figsize=(16, 9))  # крупнее холст
    min_pct = 1  # не показывать проценты для сегментов <1%

    def fmt(p):
        return f"{p:.1f}%" if p >= min_pct else ""

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,  # названия в легенде, не вокруг круга
        autopct=fmt,  # проценты внутри
        pctdistance=0.77,  # ближе к центру
        startangle=90,
        # wedgeprops=dict(width=0.4, edgecolor="white", linewidth=1),  # пончик
        wedgeprops=dict(edgecolor="white", linewidth=0.8),
        textprops=dict(fontsize=11),
    )
    # Сдвигаем область осей влево
    ax.set_position([0.5, 0.1, 0.6, 0.8])
    # [left, bottom, width, height] — доли от размеров фигуры
    ax.set(aspect="equal")

    # Легенда справа: Название: сумма (и доля)
    total = values.sum()
    legend_labels = [
        f"{n}: {v:.2f} ({v/total*100:.1f}%)" for n, v in zip(labels, values)
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Категории",
        loc="center left",
        bbox_to_anchor=(1, 0.5),  # вынести за пределы графика
        frameon=False,
        fontsize=11,
        title_fontsize=12,
    )

    plt.savefig("plots/income.png", dpi=600, bbox_inches="tight")
    plt.close()


@app.command()
def report(
    date_from: Annotated[
        str,
        typer.Option("--from", help="Начальная дата (включительно), формат YYYY-MM-DD"),
    ],
    date_to: Annotated[
        str,
        typer.Option("--to", help="Конечная дата (исключительно), формат YYYY-MM-DD"),
    ],
    uah_rate: Annotated[
        float, typer.Option("--uah-rate", help="Курс UAH за 1 PLN (например 11.53)")
    ],
):

    df = read_file()
    df_o = aggregate_outcome(df, date_from, date_to, uah_rate)
    df_i = aggregate_income(df, date_from, date_to, uah_rate)
    strip_currency_inplace_txt(df_o, df_i)

    make_pie(df_o, df_i)


if __name__ == "__main__":
    app()
