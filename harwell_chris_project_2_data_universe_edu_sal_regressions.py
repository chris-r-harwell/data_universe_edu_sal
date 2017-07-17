
# coding: utf-8

# In[2]:

import argparse
import numpy as np
import pandas as pd
import patsy
import pickle
import re
import scipy.stats as ss
import seaborn as sns
from seaborn import plt
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV
import statsmodels.api as sm
import sys


# In[3]:

get_ipython().magic('matplotlib inline')


# In[4]:

def dprint(s):
    if debug:
        print('debug: {}'.format(s))


# In[5]:

def unpickle_data(fn='my_data.pkl'):
    # Load it back.
    with open(fn, 'rb') as picklefile:
        d = pickle.load(picklefile)
    return d


# In[6]:

debug = True


# In[7]:

base_dir = '/home/crh/git/nyc17_ds12/student_submissions/projects/02-luther/harwell_chris'
data1 = unpickle_data(fn=base_dir + '/edu_sal/sal_each_page91953_91969.pkl')
data2 = unpickle_data(fn=base_dir + '/edu_sal/sal_each_page91969_92545.pkl')
data = data1
data1.update(data2)
dprint(repr(data['headers']))
dprint(repr(data['salaries']))
# Filter based on
desired_district = 'Sch Dist Of The Chathams'
dprint('number of records before {}'.format(len(data['salaries'])))
data['salaries'] = [r for r in data['salaries'] if r[4] == desired_district]
dprint('number of records after {}'.format(len(data['salaries'])))


# In[8]:

# Convert our lists to a dataframe.
df = pd.DataFrame(data['salaries'], columns=data['headers'])
dprint(repr(df))
dprint(repr(df.dtypes))


# In[9]:

# Git rid of the N/A
df2 = df.replace('N/A', np.NaN)
dprint('Len before dropna: {}'.format(len(df2)))
n = ['salary', 'experience_district', 'experience_nj', 'experience_total', 'fte']
df3 = df2.dropna(subset=n)
dprint('Len after dropna: {}'.format(len(df3)))


# In[10]:

df4 = df3
df4[n] = df3[n].apply(pd.to_numeric)


# In[11]:

for idx, val in enumerate(df4.columns):
    print('{} column: {}'.format(idx + 1, val))
dprint('row * column: {}'.format(df4.shape))


# In[12]:

print('correlations: {}'.format(df4.corr()))


# In[13]:

print('The "experience_total" and "experience_nj" columns are highly correlated (0.99).')
print('- either they are not including other states or we do not have any.')
print('The nj and district experience are also high (0.85).')


# In[ ]:




# In[ ]:




# In[14]:

sns.pairplot(df4, size=1.2, aspect=1.5)


# In[15]:

sal = df4.salary
ax = sal.hist()
ax.set_xlabel('Salary/USD')
ax.set_ylabel('Count')
ax.set_title('Salary Histogram')


# In[16]:

print('average: {:,.0f}'.format(sal.mean()))
print('middle: {:,.0f}'.format(sal.median()))
print('min,max range: {:,.0f} through {:,.0f}'.format(sal.min(), sal.max()))
print('iqr range for dispersion: {:,.0f}'.format(ss.iqr(sal)))


# In[17]:

ss.describe(sal)


# In[18]:

print('Looks skewed at 1.2 (vs. 0 for normal)')


# In[19]:

ss.normaltest(sal)


# In[20]:

df5 = df4[n]


# In[22]:

y, X = patsy.dmatrices('salary ~ experience_district ', data=df5, return_type="dataframe")
model_exp = sm.OLS(y, X)
fit_exp = model_exp.fit()
fit_exp.summary()


# In[ ]:

df4.plot(x, y)


# In[28]:

sns.lmplot('experience_district', 'salary', data=df4)
plt.title='Salary as a function of experience'


# In[25]:

sns.lmplot('experience_district', 'salary', data=df4, hue='fte')


# In[24]:

sns.lmplot('experience_district', 'salary', data=df4, hue='subcategory')


# In[ ]:




# In[20]:




# In[29]:

y, X = patsy.dmatrices('salary ~ experience_district + experience_nj + fte', data=df5, return_type="dataframe")
model = sm.OLS(y, X)
fit = model.fit()
fit.summary()


# In[22]:

fit.resid.plot(style='o', figsize=(12,8))


# In[23]:

y, X2 = patsy.dmatrices('salary ~ experience_district + experience_nj + fte', data=df5, return_type="dataframe")


# In[24]:

sm.OLS(y, X2).fit().summary()


# In[25]:

# keep fte b/c R^2 decreases


# In[26]:

y, X3 = patsy.dmatrices('salary ~ experience_district', data=df5, return_type="dataframe")
sm.OLS(y, X3).fit().summary()


# In[27]:

df6 = df5[['salary', 'experience_district', 'experience_nj', 'fte']]
lr = LinearRegression()
X = df6.iloc[:, 1:]
y = df6.iloc[:, 0]
lr.fit(X, y)
lr.score(X,y)


# In[28]:

print(lr.intercept_)


# In[29]:

print(lr.coef_)


# In[30]:

df6.to_pickle('edu_sal_df6.pkl')


# In[31]:

from sklearn.externals import joblib
joblib.dump(lr, 'edu_sal_df6_model.pkl')
df6.columns


# In[ ]:




# In[32]:

df4.subcategory.value_counts()


# In[33]:

df4.certificate.value_counts()


# In[34]:

df4.teaching_route.value_counts()


# In[35]:

df4.highly_qualified.value_counts()


# In[36]:

X = patsy.dmatrix('subcategory', data=df4, return_type='dataframe')
X.head()


# In[37]:

df7=df6.join(X)


# In[38]:

df7.head()


# In[52]:

y = df7.salary
x = df7.drop('salary', 1)


# In[53]:

lsm = sm.OLS(y, x)
fit4 = lsm.fit()
fit4.summary()
#p = fit4.params
#x = np.arange(1,3)
#ax = df7.plot(x='experience_nj', y='salary', kind='scatter')
#ax.plot(x, p.const + p.experience_nj * x + p.experience_district * x + p.ftr * x)


# In[41]:

#Including subcategory accounts for additional variability - R-squared larger.


# In[42]:




# In[44]:

# test/train validate
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import KFold


# In[45]:

# test/train split using 2/3 data for train, 1/3 for test.
lrcvr = LinearRegression()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
lrcvr.fit(X, y)
lrcvr.score(X,y)


# In[46]:

# cross validate
from sklearn.cross_validation import cross_val_score
reg = LinearRegression()
scores = cross_val_score(reg, X, y, cv=10, scoring='mean_squared_error')
print(-scores)


# In[ ]:



