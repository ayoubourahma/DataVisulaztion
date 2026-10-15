# Bank Data Visualizer

A desktop application for exploring banking data, reviewing customer and savings
activity, and producing product and savings KPIs. It loads local, semicolon-
delimited text files into Pandas DataFrames and presents the analysis through
interactive desktop tabs and charts.

## What it does

- **Executive dashboard:** summarizes customers, savings, and active users with
  KPI cards and charts.
- **Data explorer:** browse loaded datasets, search table values, select rows
  and columns, and export selected data.
- **Product and savings KPIs:** joins product and savings records by product
  code and calculates account, client, and savings metrics.
- **Customer behavior analysis:** groups customers by their monthly savings
  patterns, including full-year, partial-year, and no-savings categories.
- **Data-source and distribution views:** show dataset summaries, distributions,
  and collection methodology.
- **AI chat:** optionally ask questions about the loaded data or a customer
  profile using a locally running Ollama model.

## Technologies and techniques

- **Python** provides the application and analysis logic.
- **PyQt5** builds the native desktop interface. `QThread` workers perform data
  loading and KPI calculations without blocking the UI.
- **Pandas** loads, cleans, combines, groups, and exports tabular data.
- **NumPy** supports numeric conversion and statistical calculations.
- **Matplotlib** renders charts inside the desktop interface.
- **Ollama** (optional) provides local language-model chat; the application
  checks the local Ollama service and uses the `llama3.2:3b` model by default.
- **Requests** communicates with the local Ollama HTTP API.
- **tqdm** displays progress while loading datasets.
- **OpenPyXL** supports Excel exports. The requirements also include DuckDB.

The data-loading pipeline handles semicolon delimiters, tries common UTF-8 and
Windows encodings, normalizes whitespace and missing values, removes empty rows
and (by default) duplicates, and parses mixed date formats. Files larger than
500 MB are read in chunks. KPI calculations use Pandas merges and grouped,
vectorized aggregations.

## Requirements

- Python 3.10 or later
- Packages listed in [`requirements_desktop.txt`](./requirements_desktop.txt)
- Optional: [Ollama](https://ollama.com/) with the `llama3.2:3b` model pulled for
  AI chat

Python virtual environments, caches, and dependency lockfiles are excluded from
Git. Install the project dependencies from `requirements_desktop.txt`.

## Run the application

Create and activate a virtual environment, install the dependencies, then start
the desktop app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements_desktop.txt
python run_desktop.py
```

On startup, the app loads `.txt` files from the local `data` folder. If that
folder does not exist, it prompts you to choose a data folder. Input files
should be semicolon-delimited. Keep real customer data on your machine; data
files and generated Excel reports are excluded from Git by `.gitignore`.

To enable AI chat, install and start Ollama, then pull the default model:

```powershell
ollama pull llama3.2:3b
ollama serve
```

AI chat is optional; the rest of the desktop application can be used without
Ollama.