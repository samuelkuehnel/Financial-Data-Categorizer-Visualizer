from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def write_CSV(name, input):
    input.to_csv(name, mode='a', index=False, header=False)

def read_CSV(name):
    df = pd.read_csv(name, sep=";")
    return df

def sum_expenses(classes, data, month, year):
    result = classes.copy()
    for item in classes:
        #Filter nach verschiedenen Ausgabenklassen
        mask_1 = data["Name Zahlungsbeteiligter"].str.contains(classes[item],case=False).fillna(False)
        mask_2 = data["Verwendungszweck"].str.contains(classes[item],case=False).fillna(False)
        filtered = data.loc[mask_1 | mask_2]
        #Dataframe erstellen
        data = pd.concat([data, filtered, filtered]).drop_duplicates(keep=False)
        Path(f"Tabellen/{year}/{month}/Groups").mkdir(parents=True, exist_ok=True)
        filtered.to_excel(f"Tabellen/{year}/{month}/Groups/" + item + f"_group_{month}.xlsx", index=False, header=True)
        #Summe berechnen
        result[item] = np.round(np.sum(filtered["Betrag"]), decimals=2)
    return result, data


def finances(expenses_fix, expenses_variable, income, data, year):
    # Betrag Trennzeichen ändern
    data["Betrag"] = data["Betrag"].map(lambda a: float(np.char.replace(a,",",".")))
    #Monat herausfinden
    month = data['Monate'].iloc[0]
    #Daten spalten in + und -
    neg_data = data[data["Betrag"] < 0]
    pos_data = data[data["Betrag"] >= 0]
    #Summen berechnen
    total_income = np.round(np.sum(pos_data["Betrag"]), decimals=2)
    total_expenses = np.round(np.sum(neg_data["Betrag"]), decimals=2)
    # Ausgaben und Einnahmen aufteilen in Monate
    result_expenses_fix, neg_data = sum_expenses(expenses_fix, neg_data, month, year)
    result_expenses_variables, neg_data = sum_expenses(expenses_variable, neg_data, month, year)
    result_income, pos_data = sum_expenses(income, pos_data, month, year)
    data = pd.concat([neg_data, pos_data])
    # Nicht erkannte Buchungen festhalten
    sum_classes = {"nicht zugeordnet": np.round(np.sum(data["Betrag"]), decimals=2), "total income": total_income, "total_expenses": total_expenses, "Ergebnis": total_income + total_expenses}
    data.to_excel(f"Tabellen/{year}/{month}/remaining_{month}.xlsx", index=False, header=True)
    # Dicts zusammenfügen
    tmp = dict(result_income, **result_expenses_fix)
    tmp.update(result_expenses_variables)
    tmp.update(sum_classes)
    pd.DataFrame(tmp, index=[0]).to_excel(f"Tabellen/{year}/{month}/ordered_{month}.xlsx", index=False, header=True)
    return result_income, result_expenses_variables, result_expenses_fix, sum_classes

def split_csv_by_months(data):
    # Auszüge in Monate unterteilen
    months = np.array([''.join(list(x)[3:5]) for x in data["Buchungstag"]])
    data["Monate"] = months
    grouped = data.groupby("Monate")
    splitted = [grouped.get_group(x) for x in grouped.groups]
    return splitted

def read_months(year):
    data_months = []
    for month in range(1,10):
        try:
            data_months.append(pd.read_excel(f"Tabellen/{year}/0{month}/ordered_0{month}.xlsx"))
        except Exception as e:
            print(e)
            pass
    for month in range(10,13):
        try:
            data_months.append(pd.read_excel(f"Tabellen/{year}/{month}/ordered_{month}.xlsx"))
        except Exception as e:
            print(e)
            pass
    return data_months

def summarize_year(year, expenses_fix, expenses_variable, income):
    data_months = read_months(year)
    summarized = {"total income": 0, "total_expenses": 0, "Ergebnis": 0}
    summarized.update(dict(zip(income, np.zeros(len(income)).T)))
    summarized.update(dict(zip(expenses_fix, np.zeros(len(expenses_fix)).T)))
    summarized.update(dict(zip(expenses_variable, np.zeros(len(expenses_variable)).T)))

    for data in data_months:
        summarized["total income"] += np.sum(data["total income"])
        summarized["total_expenses"] += np.sum(data["total_expenses"])
        summarized["Ergebnis"] += np.sum(data["Ergebnis"])

        for field in income:
            summarized[field] += np.sum(data[field])
        for field in expenses_fix:
            summarized[field] += np.sum(data[field])
        for field in expenses_variable:
            summarized[field] += np.sum(data[field])
    frame = pd.DataFrame([summarized])
    frame.to_excel(f"Tabellen/{year}/{year}_summarized.xlsx")
    return frame

def plot_line_expenses(year):
    data_months = read_months(year)
    haushalt = []
    essen_gehen = []
    Kleidung = []
    diff = []
    for data in data_months:
        haushalt.append(data["Haushalt"])
        essen_gehen.append(data["Essen auswärts"])
        Kleidung.append(data["Kleidung"])
        diff.append(data["Ergebnis"])
    haushalt, essen_gehen, Kleidung, diff = np.array(haushalt), np.array(essen_gehen), np.array(Kleidung), np.array(diff)
    print(Kleidung, essen_gehen)
    months = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    fig,ax = plt.subplots()
    ax.plot(months, haushalt, label="Haushalt", linestyle="-")
    ax.plot(months, essen_gehen, label="auswärts essen", linestyle="-")
    ax.plot(months, Kleidung, label="Kleidung", linestyle="-")
    ax.plot(months, diff, label="Differenz Monatsende", linestyle="-")
    ax.set_title(f"Verlauf Kosten {year}")
    fig.set_size_inches(15,10)
    fig.tight_layout()
    fig.legend()
    fig.savefig(f"Tabellen/{year}/verlauf_kosten_{year}.png")
    fig.show()




def plot_barplot_finances(income,expenses,year):
    #split expenses
    expenses_1 = expenses.iloc[:,:int(len(expenses.columns)/2)]
    expenses_2 = expenses.iloc[:,int(len(expenses.columns)/2):]
    # Plot barplot
    fig, axes = plt.subplots(3,1)
    axes[0].bar(income.columns, income.iloc[0], color="green")
    axes[0].set_title("Einnahmen")
    axes[1].bar(expenses_1.columns, expenses_1.iloc[0], color="red")
    axes[1].set_title("Ausgaben 1")
    axes[2].bar(expenses_2.columns, expenses_2.iloc[0], color="red")
    axes[2].set_title("Ausgaben 2")
    fig.set_size_inches(15,10)
    fig.tight_layout()
    fig.savefig(f"Tabellen/{year}/summarized_{year}_barplot.png")

def plot_pieplot_finances(income,expenses,year):
    fig, axes = plt.subplots(2,1)
    axes[0].pie(income.iloc[0], labels=income.columns)
    axes[0].set_title("Einnahmen")
    del expenses["total_expenses"]
    axes[1].pie(np.abs(expenses.iloc[0]), labels=expenses.columns)
    axes[1].set_title("Ausgaben")

    fig.set_size_inches(15,10)
    fig.tight_layout()
    fig.savefig(f"Tabellen/{year}/summarized_{year}_pie.png")

def plot_finances(year):
    frame = pd.read_excel(f"Tabellen/{year}/{year}_summarized.xlsx")
    del frame[frame.columns[0]]
    income = frame.loc[:, frame.ge(0).all()]
    expenses = frame.loc[:, frame.le(0).all()]
    plot_barplot_finances(income,expenses,year)
    plot_pieplot_finances(income,expenses,year)
    plt.show()