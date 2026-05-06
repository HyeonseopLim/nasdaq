# nasdaq

Nasdaq market direction research tools.

This project is being built so that the data used for prediction is visible and inspectable.
The goal is not only to generate forecasts, but also to make it clear which raw sources,
merged tables, and derived columns are being used.

## Data source check

Run the source check script from the `invest` conda environment:

```powershell
& "C:\ProgramData\miniconda3\envs\invest\python.exe" check_data_sources.py
```

The script writes raw downloaded files and reports under `data/`. That folder is ignored by git.

## Build datasets

Create the merged datasets from the downloaded raw files:

```powershell
& "C:\ProgramData\miniconda3\envs\invest\python.exe" build_dataset.py
```

This creates:

- `data/processed/full_dataset.csv`
- `data/processed/core_dataset.csv`
- `data/processed/training_dataset.csv`
- summary markdown files for the generated datasets

## Data viewer

Run the local data viewer:

```powershell
& "C:\ProgramData\miniconda3\envs\invest\python.exe" dataset_viewer.py --port 8765
```

Then open:

- `http://127.0.0.1:8765`

The viewer includes:

- a menu showing downloaded source data and where each file came from
- a full dataset table
- a core dataset table
- plain-language explanations of each column

This is meant to keep the modeling process transparent: before training prediction models,
we can inspect the exact data sources, merged tables, and feature meanings that will be used.
