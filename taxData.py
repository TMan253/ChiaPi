# This file uses the SpaceScan.io API to fetch account history.
# See the SpaceScan.io docs here:
#   - https://docs.spacescan.io/api/address/xch_balance
#   - https://docs.spacescan.io/api/address/xch_transactions
#   - https://docs.spacescan.io/api/stats/price
#   - https://docs.spacescan.io/api/coins
#   - https://docs.coingecko.com/v3.0.1/reference/coins-id-history

import requests
import argparse
from datetime import datetime
import configparser

SPACE_SCAN_URL_PREFIX="https://www.spacescan.io/en/coin/0x"
ADDRESS = ""
CONFIG_FILE = "config.ini"
CONFIG = None
API_KEY = ""
API_OPT_SS = "SpaceScan"
API_OPT_CG = "CoinGecko"
API_CHOICE = "SpaceScan"
ARGS = None
DEBUG = True
TEST_MODE = True
CG_COIN_ID = "chia"
LIMIT = 100


def set_price_api(api):
    global API_CHOICE
    s_api = str(api).upper()

    ## match syntax isn't available until v3.10:
    # match s_api:
    #     case "S" | "SS" | "SPACESCAN" | "SPACESCAN.IO":
    #         API_CHOICE = API_OPT_SS
    #     case "C" | "CG" | "COINGECKO" | "COINGECKO.COM":
    #         API_CHOICE = API_OPT_CG
    #     case _:
    #         API_CHOICE = API_OPT_SS
    if s_api == "S" or s_api =="SS" or s_api == "SPACESCAN" or s_api == "SPACESCAN.IO":
        API_CHOICE = API_OPT_SS
    elif s_api == "C" or s_api =="CG" or s_api == "COINGECKO" or s_api == "COINGECKO.COM":
        API_CHOICE = API_OPT_CG
    else:
        API_CHOICE = API_OPT_SS

def process_cli_args():
    global ARGS, DEBUG, ADDRESS
    parser = argparse.ArgumentParser(
        description="Looks up SpaceScan.io blockchain data.",
        epilog="Thanks for using %(prog)s at your own risk! :)")
    use_opt = parser.add_argument_group("API configuration")
    use_opt.add_argument("--configure", help="optional CoinGecko API")
    use_opt = parser.add_argument_group("configuring lookup")
    # use_opt.add_argument("action", help="buy|test - live buy or simulation")
    use_opt.add_argument("-a", "--address", help="the address to look up (xch1....)")
    use_opt.add_argument("-p", "--price-api", help="the price API to use {SpaceScan (default)|CoinGecko}", default="SpaceScan")
    use_opt.add_argument("-l", "--limit", help="API fetch/batch size. Default 100", type=int, default=100)
    #opt_opt = parser.add_argument_group("options")
    parser.add_argument("-d", "--debug", action="store_true", help="toggle verbose logging")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    ARGS = parser.parse_args()
    ADDRESS = ARGS.address
    DEBUG = ARGS.debug
    if DEBUG:
        print(f"CLI args = {ARGS}")
    set_price_api(ARGS.price_api)

# '''
# ### Usage
# .\chia-pi\Scripts\python.exe .\taxData.py --help
# usage: taxData.py --help
# usage: taxData.py --version
# usage: taxData.py -a ADDRESS [-p PRICE_API] [-l LIMIT] [-d]
# usage: taxData.py --config API_KEY
#
# Looks up SpaceScan.io blockchain data.
#
# options:
#   -h, --help            show this help message and exit
#   -d, --debug           toggle verbose logging
#   --version             show program's version number and exit
#
# API configuration:
#   --configure CONFIGURE
#                         optional CoinGecko API key
#
# configuring lookup:
#   -a ADDRESS, --address ADDRESS
#                         the address to look up, such as xch1....
#   -p PRICE_API, --price-api PRICE_API
#                         the price API to use {SpaceScan (default)|CoinGecko}
#   -l LIMIT, --limit LIMIT
#                         API fetch/batch size. Default 100

def update_config_file(CONFIG_FILE, section, option, value):
    # Read the INI file.
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    # Update a value.
    old = config.get(section, option)
    print(f"Updating {CONFIG_FILE} option {section}:{option} from '{old}' to '{value}'.")
    config.set(section, option, value)

    # Write changes back to the file.
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def fetch_config_file(CONFIG_FILE, section, option):
    # Create a ConfigParser object.
    config = configparser.ConfigParser()

    # Read the INI file.
    config.read(CONFIG_FILE)

    # Set global variables, accessing values via section and option names.
    global API_KEY, CONFIG
    API_KEY = config.get(section, option).strip('"')
    CONFIG = config

    return CONFIG

# This function confirms an API response is successful.
#   If the call is not successful, it ends the program.
# @arg data - the API response JSON dictionary.
# @arg debug - a debug flag for printing the JSON.
def confirmAPISuccessOrDie(data, debug):
    if debug:
        print(f"API retuned:  {data}")
    if data["status"] != "success":
        print(f"Lookup failed with error:  {data}")
        exit(1)

# This function fetches the XCH balance of an address.
# @arg address - the Chia address to fetch from.
def getBlockExplorerBalance(address):
    url = f"https://api.spacescan.io/address/xch-balance/{address}"

    if DEBUG:
        print(f"Calling URL:  {url}")
    response = requests.get(url)
    if DEBUG:
        print(response.text)
    data = response.json()
    confirmAPISuccessOrDie(data, DEBUG)
    return data["mojo"]

# This function converts an ISO 8601 formatted timestamp string into a Unix iteger timestamp.
# @arg strISO8601 - ISO 8601 formatted UTC timestamp string (i.e., "2024-10-23T07:21:34.000Z").
# @return int Unix timestamp
def convertISO8601ToUnixTimestamp(strISO8601):
    # Parse UTC datetime object from ISO 8601 string
    utc_dt = datetime.fromisoformat(strISO8601.replace("Z", "+00:00"))

    # Convert to Unix timestamp
    unix_timestamp = int(utc_dt.timestamp())

    return unix_timestamp

# This function converts a Unix timestamp into a MS Excel timestamp.
# @arg unixTimestamp - Unix timestamp.
def convertUnixTimestampToMSExcelTimestamp(unixTimestamp):
    # Parse a local datetime object from the Unix timestamp
    dt = datetime.fromtimestamp(unixTimestamp)

    # Convert to MS Excel timestamp
    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date

# This function fetches the XCH price at a previous point in history.
# @arg cgDatestamp - the DD-MM-YYYY datestamp for when to quote historical XCH price.
# @return float
def fetchHistoricalXCHPrice_CoinGecko(cgDatestamp):
    #url = "https://api.coingecko.com/api/v3/coins/chia/history?date=21-01-2025"
    url = "https://api.coingecko.com/api/v3/coins/chia/history"

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": API_KEY
    }
    params = {
        "date": cgDatestamp,
    }

    response = requests.get(url, headers=headers, params=params)
    if DEBUG:
        print(f"API retuned:  {response.text}")
    data = response.json()
    if "error" in data:
        print(f"CoinGecko API call failed:  {data}")
        exit(1)
    return float(data["market_data"]["current_price"]["usd"])

# This function fetches the XCH price at a previous point in history.
# @arg unixTimestamp - the Unix timestamp for when to quote historical XCH price.
# @return float
def fetchHistoricalXCHPrice_SpaceScan(unixTimestamp):
    url = "https://api.spacescan.io/stats/price"
    params = {
        "currency": "USD",
        "period": int(unixTimestamp),
        "network": "mainnet"
    }

    response = requests.get(url, params=params)
    data = response.json()
    confirmAPISuccessOrDie(data, DEBUG)
    return float(data["price"])

# This function fetches the XCH price at a previous point in history.
# @arg apiChoice - the API to use for pricing data.
# @arg iso8601Timestamp - the ISO 8601 formatted timestamp string for historical quotation.
# @arg unixTimestamp - the Unix timestamp for historical quotation.
# @return float
def fetchHistoricalXCHPrice(apiChoice, iso8601Timestamp, unixTimestamp):
    if apiChoice == API_OPT_SS:
        return fetchHistoricalXCHPrice_SpaceScan(unixTimestamp)
    else:
        # CoinGecko needs DD-MM-YYYY format.
        cgDate = iso8601Timestamp[8:10] + "-" + iso8601Timestamp[5:7] + "-" + iso8601Timestamp[0:4]
        return fetchHistoricalXCHPrice_CoinGecko(cgDate)

# # This function fetches the Unix timestamp of a coin.
# #   This appears to be the creation time, but it is unclear if it changes once spent.
# def fetchCoinTimestamp(coin_id):
#     url = f"https://api.spacescan.io/coin/info/{coin_id}"
#
#     response = requests.get(url)
#     data = response.json()
#     confirmAPISuccessOrDie(data, DEBUG)
#     print(data)

# This function fetches the XCH transactions of an address.
#   Transactions are returned in reverse-chronological order.
# @arg address - the Chia address to fetch from.
# @arg apiChoice - the API to use for pricing data.
def getBlockExplorerTransactions(address, apiChoice):
    url = f"https://api.spacescan.io/address/xch-transaction/{address}"

    # Request with parameters
    totalTransactions = 0
    paginationThreshold = LIMIT
    continuePaging = True
    parameters = {
        "include_received": "true",
        "include_received_dust": "false",
        "include_send": "false",
        "include_send_dust": "false",
        "count": paginationThreshold,
        "received_cursor": 0
    }

    while continuePaging:
        # Call the API
        if DEBUG:
            print(f"Calling URL:  {url} ? {parameters}")
        response = requests.get(url, params=parameters)
        data = response.json()
        confirmAPISuccessOrDie(data, DEBUG)
        
        # Handle pagination
        if data["received_transactions"]["total_count"]:
            totalTransactions = int(data["received_transactions"]["total_count"])
        if data["received_transactions"]["next_cursor"] is None:
            continuePaging = False
        else:
            # print("Continuing to next page...")
            parameters["received_cursor"] = data["received_transactions"]["next_cursor"]
        
        # Print the transaction data
        for item in data["received_transactions"]["transactions"]:
            itemTime = item['time']
            memo = "" if item["memo"] is None else f",,,,{item['memo']}"    # skip 3 columns if there is a memo
            unixTimestamp = convertISO8601ToUnixTimestamp(itemTime)
            excelTimestamp = convertUnixTimestampToMSExcelTimestamp(unixTimestamp)
            receiptPrice = fetchHistoricalXCHPrice(apiChoice, itemTime, unixTimestamp)
            print(f"{excelTimestamp},{item['amount_xch']},${receiptPrice},${float(item['amount_xch'])*float(receiptPrice)},{SPACE_SCAN_URL_PREFIX}{item['coin_id']}{memo}")

    print(f"Total non-dust receive transactions = {totalTransactions}")

def main():
    process_cli_args()

    if ARGS.configure:
        update_config_file(CONFIG_FILE, "API", "API Key", ARGS.configure)
        exit(0)

    fetch_config_file(CONFIG_FILE, "API", "API Key")
    if DEBUG:
        print(f"API key:  {API_KEY}")

    # Query block explorer.
    print(f"Looking up address {ADDRESS}")
    totalMojo = getBlockExplorerBalance(ADDRESS)
    print(f"Total mojo: {totalMojo}")

    # Fetch tax data using preferred price API.
    getBlockExplorerTransactions(ADDRESS, API_CHOICE)


main()
