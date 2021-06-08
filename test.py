import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from datetime import datetime
from scipy.stats import ttest_ind
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate

test = pd.read_csv('test.csv')
store = pd.read_csv('store.csv')

full = test.merge(store,  on='Store')

# Recode holidays 
full = full.replace({'StateHoliday' : { 'a' : 'Public holiday', 
'b' : 'Easter holiday', 'c' : 'Christmas', 0 : 'None', '0' : 'None'}})
full = full.replace({'Assortment' : { 'a' : 'Basic', 'b' : 'Extra', 'c' : 'Extended'}})

# Recode Open Since Year
for index, value in full['CompetitionOpenSinceYear'].iteritems():
    if value == 1900:
        full['CompetitionOpenSinceYear'][index] = 1995

# Drop customers 
full = full.drop(columns=['Customers'])

# Recode day of week to strings 
full = full.replace({'DayOfWeek' : { 1 : 'Monday', 2 : 'Tuesday', 3 : 'Wednesday',
4 : 'Thursday', 5 : 'Friday', 6 : 'Saturday', 7 : 'Sunday'}})

# Add variables 
full['Month'] = pd.DatetimeIndex(full['Date']).month
full['Year'] = pd.DatetimeIndex(full['Date']).year

# Create final dataset 
final = full.iloc[:, [3, 1, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18]]
final['CompetitionDistance'] = final['CompetitionDistance'].replace(np.nan, final['CompetitionDistance'].median())
final['CompDistLog'] = np.log(final['CompetitionDistance'])
final = final.replace({'Open' : { 0 : 'Closed', 1 : 'Open'}})
final = final.replace({'Promo' : { 0 : 'Store not participating', 1 : 'Store participating'}})
final = final.replace({'Promo2' : { 0 : 'Store not participating', 1 : 'Store participating'}})
final = final.replace({'SchoolHoliday' : { 0 : 'Not affected', 1 : 'Affected'}})
final = final.replace({'Month' : { 1 : 'January', 2 : 'February', 3 : 'March', 4 : 'April', 5 : 'May',\
    6 : 'June', 7 : 'July', 8 : 'August', 9 : 'September', 10 : 'October', 11 : 'November', 12 : 'December'}})
final = final.replace({'Year' : { 2013 : '2013', 2014 : '2014', 2015 : '2015'}})
cat = ['DayOfWeek', 'Open', 'Promo', 'StateHoliday', 'SchoolHoliday', 'StoreType', 'Assortment', 'Promo2',\
    'Month', 'Year']
cat_dum = pd.get_dummies(final[cat])
# Create a list of base categories to drop 
cat_drop = ['DayOfWeek_Monday', 'Open_Closed', 'Promo_Store not participating', 'StateHoliday_None', \
            'SchoolHoliday_Not affected', 'StoreType_a', 'Assortment_Basic', 'Promo2_Store not participating', \
            'Month_January']
# Create a list of continious variables without sales 
cont_log = ['CompDistLog']
# Create a dataset
X_log = pd.concat([final[cont_log], cat_dum.drop(cat_dum[cat_drop],axis=1)], axis=1)
X_log.insert(28, 'Year_2014', 0)
X_log.insert(9, 'StateHoliday_Christmas', 0)
X_log.insert(10, 'StateHoliday_Easter', 0)
# Add year_2014


X_log.to_csv('testX.csv', index=False)