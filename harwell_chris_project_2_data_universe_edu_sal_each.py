#!/bin/env python3

from bs4 import BeautifulSoup
import argparse
import pickle
import re
import requests
import sys


base_url = 'http://php.app.com/agent/educationstaff/details/'
base_fn = 'edu_sal/sal_each_page'
# per teacher page for morris county:
# assume consecutive block...
# first:
# http://php.app.com/agent/educationstaff/details/91196
# last:
# http://php.app.com/agent/educationstaff/details/100725
# minpage=91196
# maxpage=100725
#
# per teacher page for chatham:
# http://php.app.com/agent/educationstaff/details/91969
# ...
# http://php.app.com/agent/educationstaff/details/92545
minpage=int(91953)
maxpage=int(91969)
#minpage=int(91969)
#maxpage=int(92545)
#maxpage=minpage + 1
EXPECTED_TITLE = 'NJ Teacher Salaries.*'
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


def get_employee_details(p):
    """
    Using beautiful soup parsing library, with the html5lib parser,
     summarize what we got,
     then find our table of interest,
     getting the headers without the parenthetical notes
     and then the rows and then the cell data for each row.
	<meta property="og:url" content="http://php.app.com/agent/educationstaff/details/11" />
<div id="main-feature-search-container">
		<div class="view col-md-8">
<h3><a href="/agent/educationstaff/search">NJ Teacher Salaries - UPDATED</a> - Details</h3>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>First Name</h4></div>
 <div class="col-md-8 details-field-value"><p>Andrew </div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Last Name</h4></div>
 <div class="col-md-8 details-field-value"><p>Stone</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Salary</h4></div>
 <div class="col-md-8 details-field-value"><p>$99,762</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>County</h4></div>
 <div class="col-md-8 details-field-value"><p>Atlantic</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>District</h4></div>
 <div class="col-md-8 details-field-value"><p>Atlantic City</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Experience District</h4></div>
 <div class="col-md-8 details-field-value"><p>22</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>School</h4></div>
 <div class="col-md-8 details-field-value"><p>Richmond Avenue School</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Experience New Jersey</h4></div>
 <div class="col-md-8 details-field-value"><p>22</div>
</div>

<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Primary Job</h4></div>
 <div class="col-md-8 details-field-value"><p>Social Studies Grades 5 -8</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Experience Total</h4></div>
 <div class="col-md-8 details-field-value"><p>22</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>FTE</h4></div>
 <div class="col-md-8 details-field-value"><p>0.50</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Subcategory</h4></div>
 <div class="col-md-8 details-field-value"><p>General ed</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Certificate</h4></div>
 <div class="col-md-8 details-field-value"><p>Standard certificate</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Highly Qualified</h4></div>
 <div class="col-md-8 details-field-value"><p>Not highly qualified</div>
</div>
<div class="col-md-12 details-field-container">
 <div class="col-md-4 details-field-label"><h4>Teaching Route</h4></div>
 <div class="col-md-8 details-field-value"><p>Traditional</div>
</div>
    """
    soup = BeautifulSoup(p, "html5lib")
    dprint('Fetched url {}'.format(url))
    dprint('with title {}'.format(soup.title.string))

    assert regexp_title.search(soup.title.string)
    dprint(soup.prettify)

    salaries = []
    headers = ['first', 'last', 'salary', 'county', 'district', 
               'experience_district', 'school', 'experience_nj',
               'primary_job', 'experience_total', 'fte',
               'subcategory', 'certificate', 'highly_qualified',
               'teaching_route']
    for md12 in soup.find_all("div", { "class" : "col-md-12 details-field-container"}):
        dprint(repr(md12))
        label = md12.h4.text
        value = md12.p.text
        # label = md12.find("div", { "class" : "col-md-4 details-field-label"}).text
        # value = md12.find("div", { "class" : "col-md-8 details-field-label"}).text
        if label == "First Name":
            first = value
        elif label == "Last Name":
            last = value
        elif label == "Salary":
            salary = value
        elif label == "County":
            county = value
        elif label == "District":
            district = value
        elif label == "Experience District":
            experience_district = value
        elif label == "School":
            school = value
        elif label == "Experience New Jersey":
            experience_nj = value
        elif label == "Primary Job":
            primary_job = value
        elif label == "Experience Total":
            experience_total = value
        elif label == "FTE":
            fte = value
        elif label == "Subcategory":
            subcategory = value
        elif label == "Certificate":
            certificate = value
        elif label == "Highly Qualified":
            highly_qualified = value
        elif label == "Teaching Route":
            teaching_route = value
        else:
            print('WARNING unrecognized label {} value {}.'.format(label, value))

    salary = string_to_float(salary)
    rec = [first, last, salary, county, district, experience_district,
           school, experience_nj, primary_job, experience_total, fte,
           subcategory, certificate, highly_qualified, teaching_route]
    salaries.append(rec)

    dprint('Salaries:')
    dprint(len(salaries))

    for index, item in enumerate(salaries):
        dprint('Employee idx {}: {}'.format(index, item))

    return headers, salaries


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

    data = {}
    salaries = []
    for i in range(minpage, maxpage + 1):
        url = base_url + str(i)
        fn = base_fn + str(i)
        page = get_response(url)
        headers, next_salaries = get_employee_details(page)
        salaries.extend(next_salaries)

    # Combine the data into a dictionary with
    # headers and salaries.
    data = {
            'headers': headers,
            'salaries': salaries
            }

    fn = base_fn + str(minpage) + '_' + str(maxpage) + '.pkl'
    pickle_data(data, fn=fn)
    print('Page {} written to file {}'.format(i, fn))
    old_data = unpickle_data(fn=fn)
    print(repr(old_data['headers']))
    print(repr(old_data['salaries']))
