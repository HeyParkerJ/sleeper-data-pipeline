# Goals

Grab data from sleeper.app via the [sleeper-api-wrapper](https://github.com/dtsong/sleeper-api-wrapper/) and put it in a nonrelational database for further querying in other projects

# How to run

`poetry shell` is a command used within the Poetry package manager for Python. It creates a virtual environment (virtualenv) and activates it for the current shell session. This means that any Python packages installed or used within that shell session will be isolated from the system-wide Python installation, preventing conflicts and ensuring a clean environment for your projects.

```
poetry shell
```

Inspect commands available

```
python sleeper_data_pypline/__init__.py --help
```

Run identify command
```
python sleeper_data_pypline/__init__.py identify 1 2022
```

## Design
There are two primary things that the code in this repo does:

1. Perform an ETL-like data pipeline where data is fetched from Sleeper and placed into a Mongo Atlas non-relational DB
2. Answer questions about a given league's data by querying mongo and/or sifting through data provided by Sleeper (in the case that that data is more valuable in a ad-hoc fashion) 

## Notes

I found a transaction that Sleeper's API wasn't returning for an unknown reason. I've reached out to support, but in the future, I might need to backfill this transaction myself and hope this is very, very rare.
``` python
# My notes
# TODO - Dex bid 52 on Ford this year and it's not coming up in my queries
# What we know - dex spent 52 faab on Ford who is player ID 8143
# The transaction ID for this transaction is: 1009814740870287360
```