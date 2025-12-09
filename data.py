from kaggle.api.kaggle_api_extended import KaggleApi
import pathlib

# Initialize API
api = KaggleApi()
api.authenticate()

# Define datasets to download (updated slugs for public datasets)
datasets = [
    {
        "slug": "theworldbank/education-statistics",
        "save_path": "data/global_perf",
        "unzip": True
    },
    {
        "slug": "theworldbank/world-development-indicators",
        "save_path": "data/wdi_2021",
        "unzip": True
    }
]

for ds in datasets:
    path = pathlib.Path(ds["save_path"])
    path.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {ds['slug']} to {ds['save_path']} ...")
    api.dataset_download_files(ds["slug"], path=str(path), unzip=ds["unzip"])
    print("Done.")
