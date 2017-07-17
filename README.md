**2016 Teacher Salary Data Exploration**
**School District of the Chathams**
**Chatham, NJ**
====================================

This repo contains some Python scripts used for getting
the salary data for School District of the Chathams in Chatham, NJ from [Data Universe of Asbury Park Press](http://php.app.com/agent/educationstaff/search?last_name=&first_name=&county=MORRIS&district=SCH+DIST+OF+THE+CHATHAMS&school=).

1. harwell_chris_project_2_data_universe_edu_sal_biglist_cache.py
  * abandonded, an early attempt to use google cached pages, but too few were cached and those that were 
  * if future, add a comparison for date and get the original as needed.
2. cached were old, from a different year.
harwell_chris_project_2_data_universe_edu_sal_biglist.py
  * Web scrape with Beautiful Soup to get a big list of teachers in NJ.
  * too many downloads and too little data per teacher.
3. harwell_chris_project_2_data_universe_edu_sal_each.py
  * Web scrape with Beautiful Soup to get a list of teachers in School Dist of the Chathams, NJ
  * Pulling the individual teacher pages includes more data items.
4. harwell_chris_project_2_data_universe_edu_sal_statsmodels.py
  * read in pickle, filter out just Chatham and convert to df and write to csv.
5. edu_sal/*.pkl
  * raw per page data, to allow stop/start.
  * not in repo/in .gitignore
6. edu_sal_chatham/*
  * filtered data for just Chatham in csv or odf format.
  * not in repo/in .gitignore
7. harwell_chris_project_2_regressions.ipynb
   harwell_chris_project_2_data_universe_edu_sal_regressions.ipynb
  * ipython3 notebooks with regressions
8. output/*
  * not in repo/in .gitignore
  * filtered csv from data from chatham_sal.csv
  * pickled salary from data frame edu_sal_df6.pkl
  * pickled model edu_sal_df6_model.pkl
9. harwell_chris_project_2.pdf
  * pdf of presentation, original in google present
