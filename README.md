# nasdaq

Nasdaq market direction research tools.

## Data source check

Run the source check script from the `invest` conda environment:

```powershell
& "C:\ProgramData\miniconda3\envs\invest\python.exe" check_data_sources.py
```

The script writes raw downloaded files and reports under `data/`. That folder is ignored by git.
