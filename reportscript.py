# Import packages and libraries 
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from datetime import datetime
from scipy.stats import ttest_ind
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics

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
# Check for negative sales values 
(full['Sales'] < 0 ).any()
# Check sales for outliers 
full['Sales'].describe()
plt.hist(full['Sales'], bins=20)
# The highest sales and largest amount of customers frequently lie in store 262 - may not be outliers just a large busy store 
full[full['Sales'] > 35000]
# Store 909 has highest sales - look at the distribution of its other sales to see if it is fitting
(full['Sales'][full['Store'] == 909]).describe()
(full['Sales'][full['Store'] == 57]).describe()
(full['Sales'][full['Store'] == 817]).describe()
full = full.drop([full.index[51506] , full.index[827591]])
plt.hist(full['Sales'], bins=20)


# Check all dates are within the years 
full['Date'] = pd.to_datetime(full['Date'], dayfirst=True)
# Check the dates are read in correctly 
full['Date'].dt.month
str(full['Date'].dt.date.min()) + ' to ' + str(full['Date'].dt.date.max())


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
# 1990 is major outlier in CompSinceYear, see how many rows this is the case and for what store 
(full['Store'][full['CompetitionOpenSinceYear'] == 1900]).unique()
# Recode to 1995 
for index, value in full['CompetitionOpenSinceYear'].iteritems():
    if value == 1900:
        full['CompetitionOpenSinceYear'][index] = 1995


# Check distribution of competition distance for outliers 
pd.DataFrame(full['CompetitionDistance'].describe())
plt.hist(full['CompetitionDistance'], bins=20)
(full['Store'][full['CompetitionDistance'] > 55000]).unique()


# Drop customers
full = full.drop(columns=['Customers'])


# Recode day of week to strings 
full = full.replace({'DayOfWeek' : { 1 : 'Monday', 2 : 'Tuesday', 3 : 'Wednesday',
4 : 'Thursday', 5 : 'Friday', 6 : 'Saturday', 7 : 'Sunday'}})
full['DayOfWeek'].unique()


# Deal with holiday variables (drop state holidays because it's really just a proxy for open/closed)
holiday = full[full['StateHoliday'] != 'None']
holiday[holiday['Open'] == 1]
#full = full.drop(columns=['StateHoliday'])


# Add variables 
full['Month'] = pd.DatetimeIndex(full['Date']).month
full['Year'] = pd.DatetimeIndex(full['Date']).year
full['Week'] = full['Date'].dt.week


# Create DaysSinceComp
# Combine competition month and year 
# Deal with inconsistencies in Year and Month columns 
full['CompetitionOpenSinceYear'].unique()
full['CompetitionOpenSinceMonth'].unique()
# Create new year and month variable and add it to full 
datedf = full[['CompetitionOpenSinceYear', 'CompetitionOpenSinceMonth']]
datedf = datedf.rename(columns={"CompetitionOpenSinceYear": "year", "CompetitionOpenSinceMonth": "month"})
datedf['day'] = 1
full['CompDate'] = pd.to_datetime(datedf)
# Create days since variable 
def get_days(df):
    date = df['Date']
    compdate = df['CompDate']
    if pd.notnull(compdate):
        day = (date - compdate).days
        return day
    else:
        return np.NaN
full['DaysSinceComp'] = full.apply(get_days, axis=1)
# Check for negative values and how many there are 
(full['DaysSinceComp'] <0).sum()
# Change negative values to 0 
for index, value in full['DaysSinceComp'].iteritems():
    if value < 0:
        full['DaysSinceComp'][index] = 20000
(full['DaysSinceComp'] > 20000 ).any()
(full['DaysSinceComp'] == 20000 ).sum()


# Use the DaysSince variable to change distance to 0 if the comp isn't open yet 
for index, value in full['DaysSinceComp'].iteritems():
    if value == 20000:
        full['CompetitionDistance'][index] = 78000 
(full['CompetitionDistance'] == 78000 ).sum()


# Create PromoLength
# Check that all values which are missing in PromoSinceWeek and PromoSinceYear and 0 in Promo2
full['Promo2SinceWeek'].isnull().sum()
full['Promo2SinceYear'].isnull().sum()
for index, value in full['Promo2SinceWeek'].iteritems():
    if (np.isnan(value)) == True and full['Promo2'][index] != 0:
        print(value)
# Combine PromoSinceWeek and PromoSinceYear to date varibale 
full['Promo2SinceWeek'] = full['Promo2SinceWeek'].astype("Int64")
full['Promo2SinceYear'] = full['Promo2SinceYear'].astype("Int64")
# Build funciton which combines week of year and year into datetime object 
def week_of_year_to_datetime(df):
    year = df['Promo2SinceYear']
    week = df['Promo2SinceWeek']
    if pd.notnull(year) and pd.notnull(week):
        datestring = str(year) + " " + str(week) + " 0"
        return datetime.strptime(datestring, "%Y %W %w")
    else:
        return pd.NA
full['PromoSince'] = full.apply(week_of_year_to_datetime, axis=1)
# Remove the time from the datetime
full['PromoSince'] = pd.to_datetime(full['PromoSince']).dt.date
full['PromoSince'] = pd.to_datetime(full['PromoSince'])
# Create PromoLength - days since store started participating in Promo2 
full['PromoLength'] = (full.Date - full.PromoSince)
# Extract just the days from the datetime 
def get_days(df):
    timedays = df['PromoLength']
    if pd.notnull(timedays):
        days = timedays.days
        return days 
    else:
        return np.NaN
full['PromoLength'] = full.apply(get_days, axis=1)
# Observe how many negative values there are (promotion started after current date)
(full['PromoLength'] < 0 ).sum()
for index, value in full['PromoLength'].iteritems():
    if pd.notnull(value) and value < 0:
        full['PromoLength'][index] = -1
(full['PromoLength'] == -1 ).sum()
full['PromoLength'] = full['PromoLength'].astype('Int64')


# Relitivise PromoInterval to current day 
# full['PromoInterval'].isnull().sum()
# def split_months(df):
#     months = df['PromoInterval']
#     if pd.notnull(months):
#         monlist = months.split(",")
#         return monlist 
#     else:
#         return np.NaN
# full['PromoInterval'] = full.apply(split_months, axis=1)
# sample2 = full.sample(10000)
# def give_sincecoupon(df):
#     dates = df['PromoInterval']
#     years = df['Year']
#     currentdate = df['Date']
#     if isinstance(dates, list):
#         datelist = []
#         datedifferences = []
#         for value in dates:
#             value = value.replace("Sept", "Sep")
#             date = '01' + value + str(years)
#             datelist.append(pd.to_datetime(datetime.strptime(date, '%d%b%Y')))
#         for value in datelist:
#             difference = (currentdate - value)
#             if difference.days >= 0:
#                 datedifferences.append(difference.days)
#         if not datedifferences:
#             minval = -1 
#         else:
#             minval = min(datedifferences)
#         return minval
#     else:
#         return np.NaN
# full['SinceCoupon'] = full.apply(give_sincecoupon, axis=1)


# Relaitionships between variables and Sales 
#Analyse the relationship between cat variables and sales 
fullcat = ['DayOfWeek', 'Promo2', 'Month', 'Year', 'Promo', 'StateHoliday', 'SchoolHoliday', 'StoreType', 'Assortment']
for value in fullcat:
    print(full['Sales'].groupby(full[value]).sum())

#Analyse the relationship between num variables and sales 

# Competition Distance 
plt.scatter(full['CompetitionDistance'], full['Sales'])
full['Sales'].corr(full['CompetitionDistance'])
# Plot without the outliers 
plt.scatter(full['CompetitionDistance'][full['CompetitionDistance'] < 50000], full['Sales'][full['CompetitionDistance'] < 50000], s=0.5)

# DaysSinceComp
# DaysSinceComp and Sales and see if there is a need to move furhter with the variable 
plt.scatter(full['DaysSinceComp'], full['Sales'], s=0.5)
full['Sales'].corr(full['DaysSinceComp'])
# Hard to see when there are such big outliers in the days since comp, remove these and plot again
plt.scatter(full['DaysSinceComp'][full['DaysSinceComp'] < 12500], full['Sales'][full['DaysSinceComp'] < 12500], s=0.5)
(full['Sales'][full['DaysSinceComp'] < 12500]).corr(full['DaysSinceComp'][full['DaysSinceComp'] < 12500])

# PromoLength
# Look at realtionship between PromoLength and Sales and see if there is a need to move furhter with the variable 
plt.scatter(full['PromoLength'].astype('float'), full['Sales'].astype('float'), s=1)
full['PromoLength'].astype('float').corr(full['Sales'].astype('float'))
# No point continuing, there is very little realtion between the 2 variables


# Deal with missing values (of those which realte to sales)
full.isnull().sum()
final = full.iloc[:, [3, 1, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18]]
final.isnull().sum()
# The only value with missing information is CompetitionDistance 
plt.hist(final['CompetitionDistance'], bins=25)
plt.hist(np.log(final['CompetitionDistance']), bins=25)
final['CompetitionDistance'] = final['CompetitionDistance'].replace(np.nan, final['CompetitionDistance'].median())
final['CompDistLog'] = np.log(final['CompetitionDistance'])

# Creating the dataset 
# Just categorical variables 
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
            'Month_January', 'Year_2013']
# Create a list of continious variables without sales 
cont_log = ['CompDistLog']
cont = ['CompetitionDistance']
# Create a dataset
X_log = pd.concat([final[cont_log], cat_dum.drop(cat_dum[cat_drop],axis=1)], axis=1)
X = pd.concat([final[cont], cat_dum.drop(cat_dum[cat_drop],axis=1)], axis=1)

# Model
# Create the regressor (RF in this case) with log comp distance 
rf_log = RandomForestRegressor(n_estimators=50, max_features=None)
# Fit to the X (the dataset) and y (Sales)
rf_log.fit(X_log, final['Sales'])
# Predict trust
rf_log_lbls = pd.Series(rf_log.predict(X_log))
# Create the regressor (RF in this case) with comp distance 
rf = RandomForestRegressor(n_estimators=50, max_features=None)
# Fit to the X (the dataset) and y (Sales)
rf.fit(X, final['Sales'])
# Predict trust
rf_lbls = pd.Series(rf.predict(X))
# Summaries of labels compared to true sales 
for label, series in [('RF',rf_lbls), ('RF Log Comp Dist', rf_log_lbls), ('True Sales', final['Sales'])]:
    print(label)
    print(series.describe())
# Plot 
plt.hist(final['Sales'], bins=20)
plt.hist(rf_lbls, bins=20)
plt.hist(rf_log_lbls, bins=20)
# Evaluate performance - in sample 
def make_scoring_series(score_fn):
    return pd.Series({'RF': score_fn(final['Sales'], rf_lbls),
                      'RF Log CompDist': score_fn(final['Sales'], rf_log_lbls)})

# Use the function and save results 
r2 = make_scoring_series(metrics.r2_score)
mse = make_scoring_series(metrics.mean_squared_error)
noncv_scres = pd.DataFrame({'MSE': mse,
                           'R2': r2,
                           'CV': 'Not cross validated'})

