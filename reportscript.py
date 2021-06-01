import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np

# Read in the data sets
store = pd.read_csv('store.csv')
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# Check all store values are unique and the same amount are in each data set 
pd.isnull(store).sum()
store['Store'].nunique()
pd.isnull(train).sum()
train['Store'].nunique()

# Join store and train on store number 
full = train.merge(store,  on='Store')

# Check sales are 0 when the stores are closed 
closed = full[full['Open'] == 0]
(closed['Sales'] == 0).all()

# Check sales for outliers 
full['Sales'].describe()
plt.hist(full['Sales'], bins=20)
# The highest sales and largest amount of customers frequently lie in store 262 - may not be outliers just a large busy store 
full[full['Sales'] > 38000]

# Check all dates are within the years 
full['Date'] = pd.to_datetime(full['Date'], dayfirst=True)
# Check the dates are read in correctly 
full['Date'].dt.month
str(full['Date'].dt.date.min()) + ' to ' + str(full['Date'].dt.date.max())

# Check for negative sales values 
(full['Sales'] < 0 ).any()

# Check all 0 and 1 values are 0 and 1 
for column in ['Open', 'Promo', 'SchoolHoliday', 'Promo2']:
    print(column)
    print(full[column].unique())

# Check all abcd variables are correct 
for column in ['StoreType', 'StateHoliday', 'Assortment']:
    print(column)
    print(full[column].unique())
full = full.replace({'StateHoliday' : { 'a' : 'Public holiday', 
'b' : 'Easter holiday', 'c' : 'Christmas', 0 : 'None', '0' : 'None'}})
full = full.replace({'Assortment' : { 'a' : 'Basic', 'b' : 'Extra', 'c' : 'Extended'}})

# Check values of competition since month 
for column in ['CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 'Promo2SinceWeek', 'Promo2SinceYear']:
    print(column)
    print(full[column].unique())
    
# Check distribution of competition distance for outliers 
full['CompetitionDistance'].describe()
plt.hist(full['CompetitionDistance'], bins=20)
full[full['CompetitionDistance'] > 55000]

# Drop customers
full = full.drop(columns=['Customers'])

# Recode day of week to strings 
full = full.replace({'DayOfWeek' : { 1 : 'Monday', 2 : 'Tuesday', 3 : 'Wednesday',
4 : 'Thursday', 5 : 'Friday', 6 : 'Saturday', 7 : 'Sunday'}})
full['DayOfWeek'].unique()

# Deal with holiday variables (drop state holidays because it's really just a proxy for open/closed)
full = full.drop(columns=['StateHoliday', 'SchoolHoliday'])

# Add variables 
full['Month'] = pd.DatetimeIndex(full['Date']).month
full['Year'] = pd.DatetimeIndex(full['Date']).year
full['Week'] = full['Date'].dt.week

# Combine competition month and year 
# Deal with inconsistencies in Year and Month columns 
full['CompetitionOpenSinceYear'].unique()
full['CompetitionOpenSinceMonth'].unique()

datedf = full[['CompetitionOpenSinceYear', 'CompetitionOpenSinceMonth']]
datedf = datedf.rename(columns={"CompetitionOpenSinceYear": "year", "CompetitionOpenSinceMonth": "month"})
datedf['day'] = 1
full['CompDate'] = pd.to_datetime(datedf)




d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
df['col1']

for index, value in df['col1'].iteritems():
    if value == 1:
        df['col1'][index] = np.NaN
