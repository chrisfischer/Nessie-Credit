# Nessie-Credit

Simple Banking API inspired by Capital One's Nessie, aimed at adding some missing functionality. Mainly, Nessie noteably lacks support for credit card accounts as well as balance and payment history. This RESTful API was built using Django and hosted on Heroku. Originally built for [DontBuyMe](https://github.com/chrisfischer/DontBuyMe), which was made for the Capital One Software Engineering Summit Hackathon.

The main endpoint for Nessie-Credit is [nessie-credit.herokuapp.com/api](nessie-credit.herokuapp.com/api). The following functionality is offered.

## Account Data

### Current Balance
Returns the given account number's current outstanding balance. Can be retrieved with a GET request with the parameter `value=currentBalance`.

### Balance History
Returns all monthly balance data on the given account number. Can be retrieved with a GET request with the parameter `value=balanceHistory`.

### Payment History
Returns all monthly payment data on the given account number. Can be retrieved with a GET request with the parameter `value=paymentHistory`.

### Purchase History
Returns all of the account's purchases. Provides date of purchase, vendor, and amount. Can be retrieved with a GET request with the parameter `value=purchaseHistory`.

### Skipped History
Returns all of the account's skipped purchases. Provides date of skip, vendor, and amount. Can be retrieved with a GET request with the parameter `value=skippedHistory`.

### Skipped History
Returns all of the account's skipped purchases. Provides date of skip, vendor, and amount. Can be retrieved with a GET request with the parameter `value=skippedHistory`.

### Adding new skipped purchase
Updates the database with given skipped purchase details. Can be performed with a POST request providing the fields `amount`, `vendor`, and `date`.

## Real Cost Calculations

### Real Cost
Returns the real cost (factors in expected interest payments trough past payment history and missed investment returns) of a dollar amount. Can be retrieved with a GET request with the parameter `value=realCost`. The dollar amount is passed in with `price`, and the investment return time frame is passed in through `time_reference`. Returns the following struct: 
```
{
  "dollarCost": $value$,
  "realCost": $value$,
  "investmentReturn": $value$,
  "interestCost": $value$
}
```

### Monthly Loss Breakdown
Returns the real cost losses accumulated through each month of the last calendar year. Can be retrieved with a GET request with the parameter `value=realMonthlyCostLoss`. Returns a list of the following struct:
```
{
  "date": $month$,
  "values": {
    "dollarCost": $value$,
    "realCost": $value$
  }
}
```

### Monthly Gain Breakdown
Returns the real cost gains accumulated through each month of the last calendar year by skipping purchases. Can be retrieved with a GET request with the parameter `value=realMonthlyCostGain`. Returns a list of the following struct:
```
{
  "date": $month$,
  "values": {
    "dollarCost": $value$,
    "realCost": $value$
  }
}
```
