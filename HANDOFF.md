# Handoff

## Repository

- Remote: `git@github.com:HyeonseopLim/nasdaq.git`
- Working branch: `codex/add-data-source-checker`

## What Has Been Built

1. Raw market and macro data collection checks
   - `check_data_sources.py`
   - Source verification report under `data/source_check_report.*`

2. Merged dataset builder
   - `build_dataset.py`
   - Produces:
     - `data/processed/full_dataset.csv`
     - `data/processed/core_dataset.csv`
     - `data/processed/training_dataset.csv`
     - summary markdown files

3. Local dataset viewer
   - `dataset_viewer.py`
   - `viewer/index.html`
   - Shows:
     - raw data sources and origins
     - full dataset table
     - core dataset table
     - plain-language column glossary

4. Dataset catalog / metadata
   - `dataset_catalog.py`
   - Holds core-column rules and glossary descriptions

## Current Dataset State

- Full dataset:
  - about 4,097 rows
  - 172 columns
- Core dataset:
  - about 4,097 rows
  - 106 columns

Notes:

- The merged table is aligned to QQQ trading dates.
- Lower-frequency FRED series are merged backward onto the QQQ calendar and then forward-filled.
- Prediction targets exist for:
  - `target_1d_up`
  - `target_5d_up`
  - `target_20d_up`

## Important Caveat

Publication/release lag has **not** been fully modeled yet.

That means:

- target timing is handled
- raw series merging is handled
- strict macro release-date lag handling is still a future task

Before serious backtesting, lag rules should be added for lower-frequency macro series.

## Run Commands

### Data source check

```powershell
cd "C:\hs\personel\nasdaq\nasdaq"
& "C:\ProgramData\miniconda3\envs\invest\python.exe" check_data_sources.py
```

### Build datasets

```powershell
cd "C:\hs\personel\nasdaq\nasdaq"
& "C:\ProgramData\miniconda3\envs\invest\python.exe" build_dataset.py
```

### Run data viewer

```powershell
cd "C:\hs\personel\nasdaq\nasdaq"
& "C:\ProgramData\miniconda3\envs\invest\python.exe" dataset_viewer.py --port 8765
```

Then open:

- `http://127.0.0.1:8765`

## Suggested Next Steps

1. Add publication lag rules for macro data
2. Regenerate lag-aware full/core datasets
3. Build baseline modeling scripts
   - Logistic Regression
   - RandomForest
   - optionally XGBoost/LightGBM
4. Compare `core` vs `full`
5. Add metrics/reporting
   - Accuracy
   - AUC
   - Brier score
   - calibration

## Intent / Transparency

This project is meant to be transparent about:

- which raw datasets are used
- where they came from
- how they are merged
- what each column means

The viewer and README were added specifically so future modeling work can be inspected instead of treated as a black box.
