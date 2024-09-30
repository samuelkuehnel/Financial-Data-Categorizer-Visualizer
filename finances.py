from methods import *
from data import expenses_fix, expenses_variable, income
import click
import matplotlib.pyplot as plt
import pandas as pd
import warnings
import numpy as np
import tkinter as tk

@click.command()
@click.option(
    "--year",
    required=True,
    help="year where finances should be analyzed",
)
def run(year):
    data = read_CSV(f"./{year}.csv")
    n_split = split_csv_by_months(data)
    sorted_data = []
    for frame in n_split:
       sorted_data.append(finances(expenses_fix, expenses_variable, income, frame, year))
    frame_summarized = summarize_year(year, expenses_fix.keys(), expenses_variable.keys(), income.keys())
    plot_finances(year)
    plot_line_expenses(year)
    return sorted_data, frame_summarized

def create_GUI():
    root= tk.Tk()
    canvas1 = tk.Canvas(root, width=400, height=300)
    canvas1.pack()
    entry1 = tk.Entry(root) 
    canvas1.create_window(200, 140, window=entry1)



if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sorted_data, summarized = run()
