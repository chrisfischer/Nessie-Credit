'''
API - offers a way to pull data from the database:
    fields: fields from models.Listing to be queried

    plot: Lets you create aliases for variables. Need the same number of aliases as fields. Also filters null values.

    groupBy: currently only groups by location, will average the given field(s) by a 0.001 square degree regions and return either: (1) a tuple of the average value and coordinates if only one field was passed in, or (2) a tuple of coordinates and a dictionary of field name -> average value. Also filters null values.

    Other options:
        length(field): will create an alias length_field with the length of that character field

'''

import operator
from collections import OrderedDict

from .values import *

from bson.json_util import dumps
from pymongo import MongoClient, DESCENDING

import requests
import json

def parse_get(o):
    key = o['key'][0]
    if key != apiKey:
        return null

    account = o['account'][0]
    if account != creditId:
        return null

    value = o['value'][0].split(' ')
    if len(value) != 1:
        return null
    field = value[0]

    client = MongoClient("mongodb://admin:password1@ds251287.mlab.com:51287/heroku_x5rvthjk")
    db = client.get_default_database()

    # return list of numerical fields
    if (field == 'currentBalance'):
        balances = db['balance-history']
        cursor = balances.find({}, {'balance': True, '_id': False}).sort([('date', DESCENDING)]).limit(1)
        return list(cursor)[0]['balance']

    if (field == 'balanceHistory'):
        return get_sorted_balance_history(db)

    if (field == 'paymentHistory'):
        return get_sorted_payment_history(db)

    if (field == 'purchaseHistory'):
        payments = db['purchase-history']
        cursor = payments.find()
        toReturn = []
        for d in cursor:
            toReturn.append({
                'date': d['date'],
                'vendor': d['vendor'], 
                'price': d['price'],
                'id': str(d['_id'])
            })
        toReturn.sort(key=lambda d: d['date'], reverse=True)
        return toReturn

    if (field == 'skippedHistory'):
        payments = db['skipped-history']
        cursor = payments.find()
        toReturn = []
        for d in cursor:
            toReturn.append({
                'date': d['date'],
                'vendor': d['vendor'], 
                'price': d['price'],
                'id': str(d['_id'])
            })
        toReturn.sort(key=lambda d: d['date'], reverse=True)
        return toReturn

    if (field == 'realMonthlyCostLoss'):
        month = o['month'][0]
        return monthly_sum(db, 'purchase-history', month)

    if (field == 'realMonthlyCostGain'):
        month = o['month'][0]
        return monthly_sum(db, 'skipped-history', month)
      
    if (field == 'realCost'):
        value = o['value'][0]
        return individual_cost(db, value)

def individual_cost(db, value):
    data = {
        "cost":50,
        "timeReference":30,
        "determinantFundData":"vfinx.csv",
        "balance": "200",
        "interest": "18",
        "payment": "20"
    }
    r = requests.post('https://v2239ujovd.execute-api.us-east-1.amazonaws.com/prod/actualRealCost1', data=json.dumps(data), headers={'Content-type': 'application/json'})
    op_cost = r.json()['opportunityCost']
    real_cost = op_cost['realCost']
    investment_return = op_cost['investmentReturn']
    intrest_cost = op_cost['interest']

    return { 
        'dollarCost': purchase_sum, 
        'realCost': real_cost, 
        'investmentReturn': investment_return, 
        'intrestCost': intrest_cost 
        }

def monthly_sum(db, key, month):
    previous_month = get_previous_month(month + '-01')
    payments = db[key]
    cursor = payments.find()
    purchase_sum = 0.0
    for d in cursor:
        if d['date'][:7] == month:
            purchase_sum += float(d['price'])

    data = {
         "stockData": "swppx.csv",
         "balance": get_months_balance(db, previous_month),
         "interest": "18",
         "payment": get_average_payment(db) * purchase_sum,
         "currentDate": previous_month,
         "purchaseDate": month + "-01",
         "itemCost": purchase_sum
        }

    r = requests.post('https://v2239ujovd.execute-api.us-east-1.amazonaws.com/prod/actualRealCost1', data=json.dumps(data), headers={'Content-type': 'application/json'})
    print(r.json())
    real_cost = r.json()['opportunityCost']['realCost']
    return { 'dollarCost' : purchase_sum, 'realCost': real_cost }


def get_months_balance(db, date):
    month = date[:7]
    balances = db['balance-history']
    cursor = balances.find({'date': month})
    return list(cursor)[0]['balance']

def get_average_payment(db):
    b = get_sorted_balance_history(db)
    p = get_sorted_payment_history(db)
    difference_sum = 0.0
    count = 0
    for (date1, balance), (date2, payment) in zip(b.items(), p.items()):
        difference_sum += ((balance - payment)/balance)
        count += 1
    return difference_sum/count

def get_sorted_balance_history(db):
    balances = db['balance-history']
    cursor = balances.find({}, { "_id": False})
    toReturn = {}
    for d in cursor:
        toReturn[d['date']] = d['balance']
    l = sorted(toReturn.items(), key=operator.itemgetter(0))
    d = OrderedDict()
    for t in l:
        d[t[0]] = t[1]
    return d

def get_sorted_payment_history(db):
    payments = db['payment-history']
    cursor = payments.find({}, { "_id": False})
    toReturn = {}
    for d in cursor:
        toReturn[d['date']] = d['payment']
    l = sorted(toReturn.items(), key=operator.itemgetter(0))
    d = OrderedDict()
    for t in l:
        d[t[0]] = t[1]
    return d

def get_previous_month(s):
    year = s[:4]
    month = s[5:7]
    day = s[8:]
    if month == '01':
        month = '12'
        year = str(int(year) - 1)
    else:
        month = str(int(month) - 1)
    return year + '-' + month + '-' + day

def parse_post(o):
    key = o['key'][0]
    if key != apiKey:
        return null

    account = o['account'][0]
    if account != creditId:
        return null
    try:
        new_purchase = {
            'date': o['date'][0],
            'price': float(o['price'][0]),
            'vendor': o['vendor'][0],
        }

        client = MongoClient("mongodb://admin:password1@ds251287.mlab.com:51287/heroku_x5rvthjk")
        db = client.get_default_database()
        payments = db['skipped-history']
        payments.insert(new_purchase)

        return 200
    except:
        return 400

