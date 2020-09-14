from datetime import date
from calendar import Calendar
from flask import url_for, request, g
import json
import os
import copy
import csv
from zipfile import ZipFile
import urllib.request as url
import urllib.error as url_errors

# Dictionary to link choices to icons
label_icons = {
    'Shopping' : 'shopping_cart',
    'Food & Beverages' : 'fastfood',
    'Travel':'emoji_transportation',
    'Entertainment': 'sports_esports',
    'Bills':'receipt_long', 
    'Gifts & Donations':'redeem',
    'Healthcare':'healing', 
    'Investment':'analytics', 
    'Others':'request_page',
    'Salary': 'payments',
    'Gifts': 'redeem',
    'Interest': 'account_balance',
    'Selling': 'monetization_on',
    'Awards': 'military_tech'
}

# Dictionary to associate colors' names
colors_mapper = {
    'purple': 'rgba(75, 0, 130, 0.6)', 
    'orange':'rgba(255, 165, 0, 0.8)',
    'blue':'rgba(65, 105, 255, 0.8)',
    'yellow':'rgba(255, 255, 49, 0.8)',
    'green':'rgba(50, 205, 50, 0.8)',
    'grey':'rgba(47, 79, 79, 0.8)',
    'red':'rgba(250, 128, 114, 0.8)',
    'turqoise':'rgba(0, 206, 209, 0.8)',
    'brown':'rgba(178, 34, 34, 0.8)'
}

# Dictionary to associate colors of categories choices
label_colors = {
    'Shopping' : colors_mapper['purple'],
    'Food & Beverages' : colors_mapper['orange'],
    'Travel': colors_mapper['blue'],
    'Entertainment': colors_mapper['turqoise'],
    'Bills':colors_mapper['grey'], 
    'Gifts & Donations': colors_mapper['yellow'],
    'Healthcare': colors_mapper['red'], 
    'Investment': colors_mapper['green'], 
    'Others': colors_mapper['brown'],
    'Salary': colors_mapper['green'],
    'Gifts': colors_mapper['yellow'],
    'Interest': colors_mapper['grey'],
    'Selling': colors_mapper['red'],
    'Awards': colors_mapper['turqoise']
}

# In case the API fails, dictionary to hardcode exchange rates into the program
hardcoded_rates = {
    'KHR':{'symbol':'៛', 'rates':'4100.00'},
    'EUR':{'symbol':'€', 'rates':'0.85'},
    'USD':{'symbol':'$', 'rates':'1.0'},
    'CAD':{'symbol':'$', 'rates':'1.30'}
}

def getfilter():
    try:
        filter = request.cookies.get('filter')
        if not filter:
            filter = 'USD'
    except:
        filter = 'USD'
    return filter
    
def make_exrate_dict(rates):
    """Function to create a dictionary of currency code, symbols and rate"""
    try:
        curr_code = ['KHR', 'EUR']
        curr_code2 = ['USD', 'CAD']
        API_KEY = os.environ.get('API_KEY')
        data_rates = json.load(url.urlopen(f"https://free.currconv.com/api/v7/convert?apiKey={API_KEY}&q=USD_KHR,USD_EUR&compact=ultra"))  
        data_rates2 = json.load(url.urlopen(f"https://free.currconv.com/api/v7/convert?apiKey={API_KEY}&q=USD_CAD,USD_USD&compact=ultra"))
        symbols = json.load(url.urlopen(f"https://free.currconv.com/api/v7/currencies?apiKey={API_KEY}"))
        for code in curr_code:
            rates.update({
                code : {
                    'symbol': symbols['results'][code]['currencySymbol'],
                    'rates': round(data_rates[f'USD_{code}'], 2)
                }
            })  
        for code2 in curr_code2:
            rates.update({
                code2 : {
                    'symbol': symbols['results'][code2]['currencySymbol'],
                    'rates': round(data_rates2[f'USD_{code2}'], 2)
                }
            }) 
    except url_errors.HTTPError and url_errors.URLError:
        rates.update(hardcoded_rates)
    return rates

def convert_currency_float(value, code, rates):
    """Converts any value into a currency float for calculations"""
    ex_rate = float(rates[code]['rates'])
    value_inCurr = float(value * ex_rate)
    return float(round(value_inCurr, 2))

def convert_usd(value, code, rates):
    """Converts any value into USD float for calculations"""
    ex_rate = float(rates[code]['rates'])
    value_inUSD = float(value / ex_rate)
    return float(round(value_inUSD, 2))

def make_records_dict(records, rates):
    newrecords = copy.deepcopy(records)
    ex_rate = float(rates[g.code]['rates'])
    for key, record in newrecords.items():
        for k, v in record.items():
            record[k] = round((v * ex_rate), 2)
    return newrecords

def make_today_transactions(sqlquery):
    """Convert SQLAlchemy query into a dictionary based on category of transactions"""
    result = {}
    for query in sqlquery:
        if query.category in result.keys():
           result[query.category] += query.amount
        else:
           result.update({query.category : query.amount})
    print(result)
    return result

def find_weekrange(date):
    """Returns a week range a date is in""" 
    cal = Calendar().monthdatescalendar(date.year, date.month)
    for x in range(len(cal)):
        if date in cal[x]:
            return f"{cal[x][0].strftime('%d/%m')}-{cal[x][-1].strftime('%d/%m/%Y')}"
            
def find_month_complete(date):
    """Return a list of date objects from Monday to Sunday in a given month of a date""" 
    cal = Calendar().monthdatescalendar(date.year, date.month)
    return [cal[n][i] for n in range(len(cal)) for i in range(len(cal[n]))]

def find_month_weekrange(date):
    """Returns a list of week ranges from Monday to Sunday in a given month of a date"""
    cal = Calendar().monthdatescalendar(date.year, date.month)
    return [f"{cal[n][0].strftime('%d/%m')}-{cal[n][-1].strftime('%d/%m/%Y')}" for n in range(len(cal))]

def write_to_csv(dictionary, header, csvfile):
    """Writes a dictionary from SQL query and list of headers into a csv file"""
    with open(csvfile, 'w') as a:
        writer = csv.DictWriter(a, delimiter=';', fieldnames=header, lineterminator='\n')
        writer.writeheader()
        for d in dictionary:
            writer.writerow(
                dict(
                    (k, v) for k, v in d.items()
                )
            )
    return csvfile

def write_to_zip(zipfile, filelist):
    """Write a list of files into a zip file"""
    with ZipFile(zipfile, 'w') as zipObj:
        for file in filelist:
            zipObj.write(file)