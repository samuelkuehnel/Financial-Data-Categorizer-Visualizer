# Financial-Data-Categorizer-Visualizer

This Python tool helps you analyze your finances. You can Import your CSV transaction data, categorize spending, and generate visualizations (bar charts, pie charts, etc.) to understand your income and expenses.

## Structure

**Classification**: Spending and income categories are set in [data.py](./src/data.py). There are currently three dictionaries for income, static expenses like rent (_expenses_fix_) and variable expenses like groceries or clothing (_expenses_variable_). In theses dictionaries you can define classes by adding new keys and values. The key represents the category name and the value contains a list of keywords, that will be used to classify the expenses read by the program. All keywords need to be separated via `|`.

**Methods**: In [methods.py](./src/methods.py) all functionality is provided for the main execution.

**Finance Manager**: The tool can be executed with [finances.py](./src/finances.py). As a command line argument need to pass the year that should be analyzed.
