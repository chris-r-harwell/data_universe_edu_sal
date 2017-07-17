#!/bin/env python3


import argparse
import numpy as np
import pandas as pd
import pickle
import re
import seaborn as sns
from seaborn import plt
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV
import statsmodels.api as sm
import sys


%matplotlib inline


def dprint(s):
    if debug:
        print('debug: {}'.format(s))


def unpickle_data(fn='my_data.pkl'):
    # Load it back.
    with open(fn, 'rb') as picklefile:
        d = pickle.load(picklefile)
    return d


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="turn on debug", type=bool)
    args = parser.parse_args()
    if args.debug:
        print("debug turned on")
        debug = True
    else:
        debug = False
    data1 = unpickle_data(fn='edu_sal/sal_each_page91953_91969.pkl')
    data2 = unpickle_data(fn='edu_sal/sal_each_page91969_92545.pkl')
    data = data1
    data1.update(data2)
    dprint(repr(data['headers']))
    dprint(repr(data['salaries']))
    # Filter based on
    desired_district = 'Sch Dist Of The Chathams'
    dprint('number of records before {}'.format(len(data['salaries'])))
    data['salaries'] = [r for r in data['salaries'] if r[4] == desired_district]
    dprint('number of records after {}'.format(len(data['salaries'])))
    """
    0 first                   object
    1 last                    object
    2 salary                 float64
    3 county                  object
    4 district                object
    5 experience_district     object
    6 school                  object
    7 experience_nj           object
    8 primary_job             object
    9 experience_total        object
    10 fte                     object
    11 subcategory             object
    12 certificate             object
    13 highly_qualified        object
    14 teaching_route          object
    """

    # Convert our lists to a dataframe.
    df = pd.DataFrame(data['salaries'], columns=data['headers'])
    dprint(repr(df))
    dprint(repr(df.dtypes))

    # Convert the string 'N/A' into a numpy not a number
    # and then just drop those rows.
    df2 = df.replace('N/A', np.NaN)
    # df2 = df.applymap(lambda x: np.nan if x == 'N/A' else x)
    df2.to_csv(path_or_buf='chatham_sal.csv', header=True)
    dprint('Len before dropna: {}'.format(len(df2)))
    df3 = df2.dropna(subset=['salary', 'experience_district', 'experience_nj', 'experience_total'])
    dprint('Len after dropna: {}'.format(len(df3)))

    # Make sure we have numeric types rather than strings or something.
    n = ['salary', 'experience_district', 'experience_nj', 'experience_total', 'fte']
    df4 = df3
    df4[n] = df3[n].apply(pd.to_numeric)

    dprint('columns: {}'.format(df4.columns))
    dprint('row * column: {}'.format(df4.shape))
    print('correlations: {}'.format(df4.corr()))
    print('experience_total is highly correlated with experience nj - either they are not including other states or we do not have any')
    sns.pairplot(df4, size=1.2, aspect=1.5)

    Y = df4.salary
    X1 = df4.experience_district
    X2 = df4.experience_nj
    # X3 = df4.experience_total
    # for X in X1, X2, X3:
    #    dprint('Before add constant {}'.format(repr(X)))
    #    X = sm.add_constant(X)
    #    dprint('After add constant {}'.format(repr(X)))
    #    model = sm.OLS(Y, X)
    #    results = model.fit()
    #    print('results:')
    #    print(repr(results.summary()))
    #    print(' params:')
    #    print(repr(results.params))
    #    print(' rsquared:')
    #    print(repr(results.rsquared))
    #    print(' tvalues:')
    #    print(repr(results.tvalues))
    #    print(' t_test:')
    #    print(repr(results.t_test([1, 0])))
    #    print(' f_test:')
    #    print(repr(results.f_test(np.identity(2))))
