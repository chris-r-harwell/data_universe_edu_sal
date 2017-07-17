#!/bin/env python3

from bs4 import BeautifulSoup
import argparse
import pickle
import re
import requests
import sys


base_url = 'http://php.app.com/agent/educationstaff/search/page:'
base_cache = 'http://webcache.googleusercontent.com/search?q=cache:'
base_fn = 'edu_sal_google_cache/sal_biglist_page'
#url = 'http://php.app.com/agent/educationstaff/search/page:2'
# where :2 is page, expect 13873 pages.
#maxpage = 2
maxpage = 13873
EXPECTED_TITLE = 'New Jersey Public School Teacher Salaries'
regexp_title = re.compile(EXPECTED_TITLE)
regexp_notes = re.compile('\[.*\]')
regexp_drop_lower_range = re.compile('[0-9]+-')


def dprint(s):
    if debug:
        print('debug: {}'.format(s))


def get_response(url):
    """
    Using the requests library get a particular url, checking that we got
    the page OK by making sure the code is 200,
     then, just stuff the text itself, the html, into the page for passing
     along to beautiful soup.
    """
    response = requests.get(url)
    dprint('Getting url {}'.format(url))
    if response.status_code != 200:
        print('Error: Got response {}, not expected 200.'.format(
            response.status_code))
        sys.exit(1)

    p = response.text
    # dprint(p)
    return p


def string_to_float(s):
    if isinstance(s, str):
        new = s.replace(',', '').replace('+', '').replace('<', '').replace('$', '')

        if '-' in new:
            new = regexp_drop_lower_range.sub('', new)

        dprint('Before: {} After: {}'.format(s, new))

        if len(new) > 0:
            return float(new)
        else:
            return 'NAN'


def get_header_and_salary_data(p):
    """
    Using beautiful soup parsing library, with the html5lib parser,
     summarize what we got,
     then find our table of interest,
     getting the headers without the parenthetical notes
     and then the rows and then the cell data for each row.
    """
    soup = BeautifulSoup(p, "html5lib")
    dprint('Fetched url {}'.format(url))
    dprint('with title {}'.format(soup.title.string))

    assert regexp_title.search(soup.title.string)

    table_of_interest = soup.find("table", {"class" : "table table-striped table-condensed"})
    dprint('table_of_interest: {}'.format(table_of_interest))

    headers_of_table_of_interest = table_of_interest.find_all('th')

    headers = []
    dprint('Headers:')
    for index, element in enumerate(headers_of_table_of_interest):
        dprint('Header idx {}: {}'.format(index, element.text))
        headers.append(element.text.replace('\n(million US$)', ''))

    salaries = []  # use a list of lists
    dprint('Rows:')
    rows_of_table_of_interest = table_of_interest.find_all('tr')[1:]
    for index_e, element in enumerate(rows_of_table_of_interest):
        dprint('Row idx {}: {}'.format(index_e, element))
        this_salary = []
        for index_d, data in enumerate(element.find_all('td')):
            dprint('Salary table data idx {}: data.text: {}'.format(index_d, data.text))
            dprint('Salary table data idx {}: data:{}'.format(index_d, data))
            # clean the notes out.  [41][unreliable source?]
            if '[' in data.text:
                dprint('noticed square bracket')
                new = regexp_notes.sub('', data.text)
                dprint('old: {}'.format(data.text))
                dprint('new: {}'.format(new))
                this_salary.append(new)
            else:
                this_salary.append(data.text)
        salaries.append(this_salary)

    for g in salaries:
        dprint('Checking {} {}'.format(g[0], g[1]))
        g[6] = string_to_float(g[6])

    dprint('Salaries:')
    dprint(len(salaries))

    for index, item in enumerate(salaries):
        dprint('Employee idx {}: {}'.format(index, item))

    # Combine the data into a dictionary with
    # headers and salaries.
    data = {
            'headers': headers,
            'salaries': salaries
            }
    return data


def pickle_data(d, fn='best_selling_vg.pkl'):
    # Save that data to a pickled file.
    with open(fn, 'wb') as picklefile:
        pickle.dump(d, picklefile)


def unpickle_data(fn='best_selling_vg.pkl'):
    # Load it back.
    with open(fn, 'rb') as picklefile:
        d = pickle.load(picklefile)
    return d


if __name__ == '__main__':
    """ Use argparse to get a filename as the first argument. """
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="turn on debug", type=bool)
    args = parser.parse_args()
    if args.debug:
        print("debug turned on")
        debug = True
    else:
        debug = False

    data = []
    for i in range(1, maxpage + 1):
        url = base_cache + base_url + str(i)
        fn = base_fn + str(i) + '.pkl'
        page = get_response(url)
        #data.extend(get_header_and_salary_data(page))
        data = (get_header_and_salary_data(page))
        pickle_data(data, fn=fn)
        print('Page {} written to file {}'.format(i, fn))
        # old_data = unpickle_data(fn=fn)
        # print(repr(old_data['headers']))
        # print(repr(old_data['salaries']))
