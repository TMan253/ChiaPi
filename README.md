# ChiaPi
Miscellaneous scripts for Raspberry Pi Chia farmers


# taxData.py
A tool for sourcing transaction cost bases information from SpaceScan.io. This script is intended for miners receiving payouts and supports optional CoinGecko pricing.

## Disclaimer
This tool is without guarantees or warranty and only available on an as is basis.  This tool is used at your own risk!

## Usage
```
usage: taxData.py [-h] [--configure CONFIGURE] [-a ADDRESS] [-p PRICE_API] [-l LIMIT] [-d] [--version]

Looks up SpaceScan.io blockchain data.

options:
  -h, --help            show this help message and exit
  -d, --debug           toggle verbose logging
  --version             show program's version number and exit

API configuration:
  --configure CONFIGURE
                        optional CoinGecko API key

configuring lookup:
  -a ADDRESS, --address ADDRESS
                        the address to look up (xch1....)
  -p PRICE_API, --price-api PRICE_API
                        the price API to use {SpaceScan (default)|CoinGecko}
  -l LIMIT, --limit LIMIT
                        API fetch/batch size. Default 100
```

## Creating an API key
This tool optionally uses a CoinGecko API key.  To create an API key:
1. Log into https://www.coingecko.com/en/developers/dashboard
2. Click the `Add New key` button.
3. Name the key.  Click `Create & download`.
4. Retain the key in a safe manner - it is a bearer token allowing access to your account!

### Runtime setup for Windows
Use the following steps to deploy on a Windows host:
1. git clone https://github.com/TMan253/ChiaPi.git
2. cd ChiaPi
3. python -m venv chia-pi  # Create a virtual environment
4. .\chia-pi\Scripts\activate.bat
5. pip --version
6. python -m pip install --upgrade pip
7. pip --version
8. python -m pip install requests argparse
9. python taxData.py --address "xch1..."
10. Optional for CoinGecko data:  notepad.exe .\config.ini
11. Optional for CoinGecko data:  add these contents, substituting your API key within the quotation marks, and then save the file and exit:
```
[API]
API Key = "yourKeyHere"
```


### Docker dev environment setup
`TBD`

### Dev environment setup
Use the following steps to create a local development environment:
1. git clone https://github.com/TMan253/ChiaPi.git
2. cd ChiaPi
3. python -m venv chia-pi  # Create a virtual environment
4. source chia-pi/bin/activate   # for Linux, or for Windows:  chia-pi\Scripts\activate.bat
5. pip --version
6. .\chia-pi\Scripts\python.exe -m pip install --upgrade pip
7. pip --version
8. .\chia-pi\Scripts\python.exe -m pip install requests argparse
9. .\chia-pi\Scripts\python.exe .\taxData.py --address "xch1..."
10. Optional for CoinGecko data:  vi .\config.ini
11. Optional for CoinGecko data:  add these contents, substituting your API key within the quotation marks, and then save the file and exit:
```
[API]
API Key = "yourKeyHere"
```
