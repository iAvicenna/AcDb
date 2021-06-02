#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import json
from test_fun import deep_eq
current_dir = os.path.abspath('')
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from AcDb import db_experiment_list, db_anti_list


# In[2]:


# loading experiments, antigens and sera
# these inherit from db_list which is essentially a list
# of dictionaries with some extra checks during appending,
# inserting etc to guarantee that data you are trying to enter
# satisfies certain criteria such as uniqueness of ID.

database_dir = current_dir + '/test_datasets/'

exp_list = db_experiment_list(database_dir+'test_results.json')
antigen_list = db_anti_list(database_dir+'test_antigens.json')
serum_list = db_anti_list(database_dir+'test_sera.json')


# In[3]:


# we will first experiment with manipulations of exp_list
print(exp_list)


# In[4]:


# lets take the first entry from this dataset and try appending
# it as a new entry
entry = exp_list[0].copy()

# it should have a unique id so below will fail
try:
    exp_list.append(entry)
except ValueError as e:
    print(e)
    


# In[5]:


# one can generate an id using the function below and it should work fine
entry['id'] = exp_list.generate_new_id()  # hint this is a base property of db_list from which the 
                                          # experiment and anti lists inherit from
exp_list.append(entry)


# In[6]:


# one can actually create a new entry using the create_entry function.
# Here you dont need to supply an id as the list will automatically 
# create a unique id. However it is required to have a name, description
# and results field. Results fields also needs to pass some basic checks
# as demonsrated below.

try:
    exp_list.create_entry(ename='New entry', edesc='New entry created to fail', eresults=[])
except AssertionError as e:
    print(e, end='\n\n')

try:
    exp_list.create_entry(ename='New entry', edesc='New entry created to fail', eresults=['Stop pestering me'])
except AssertionError as e:
    print(e, end='\n\n')
 
try:
    exp_list.create_entry(ename='New entry', edesc='New entry created to fail', eresults=[{'please':'I will put my results later I promise'}])
except AssertionError as e:
    print(e, end='\n\n')
 

results = [{'antigen_ids':['AAAAAA'], 'serum_ids':['BBBBBB'], 'date':'now', 
       'file':'fake.csv', 'conducted_by':'Sina', 'assay':'HI', 'titers':[['put later']]}]    

try:
    exp_list.create_entry(ename='New entry', edesc='New entry created to fail', eresults=results)
except AssertionError as e:
    print(e, end='\n\n')
 


# In[7]:


# now a correct entry

results = [{'antigen_ids':['AAAAAA'], 'serum_ids':['BBBBBB'], 'date':'now', 
       'file':'fake.csv', 'conducted_by':'Sina', 'assay':'HI', 'titers':[['1260']]}]
exp_list.create_entry(ename='New entry', edesc='New entry created to fail', eresults=results)


# In[8]:


# once you are done entering your data (correctly), you can save it as a json file
# to check read and write functionalities lets try reloading, saving and passing 
# it through a deep equality test (i.e a decode-encode = identity test)
# however writing experiment_lists needs to pass a cross_check which is discussed later
# so for now I will just turn it off

exp_list1 = db_experiment_list(database_dir+'test_results.json')
exp_list1._cross_check_required=False
exp_list1.write(database_dir+'test_results2.json')

#to do the test on a lower level, we will read the files with json
with open(database_dir+'test_results.json', 'r') as fileobj:
            exp_list1 = json.load(fileobj)

with open(database_dir+'test_results2.json', 'r') as fileobj:
            exp_list2 = json.load(fileobj)

print(deep_eq(exp_list1, exp_list2))


# is this deep_eq function working correctly?
exp_list1[0]['name']='What??'
print(deep_eq(exp_list1, exp_list2))


# In[9]:


# lets play around with antigen and sera lists now
# now lets load antibody and serum lists

#lets try to add an existing entry again
entry = antigen_list[0].copy()

try:
    antigen_list.append(entry)
except ValueError as e:
    print(e)


# In[10]:


# lets change its id and it should work:

entry['id'] = antigen_list.generate_new_id()
antigen_list.append(entry)


# In[11]:


# as with experiment lists you can create entries
print(antigen_list[-1])
antigen_list.create_entry(elong='Some antigen')
print(antigen_list[-1])


# In[12]:


# finally experiment lists have some cross-checking facility
# for this you provide the cross_check function with antigen and serum 
# lists and the functions tests if these are compatible.
# a cross-check is required for writing experiment lists to files

exp_list = db_experiment_list(database_dir+'test_results.json', name='test experiment list')
antigen_list = db_anti_list(database_dir+'test_antigens.json')
serum_list = db_anti_list(database_dir+'test_sera.json')

try:
    exp_list.write(database_dir+'test_results3.json')
except ValueError as e:
    print(e)


# In[13]:


exp_list.cross_check(antigen_list, serum_list)
exp_list.write(database_dir+'test_results3.json')


# In[14]:


# works fine for now. Lets break it by adding a new result whose antigens
# and sera dont appear in the antigen and sera list

result = [{'antigen_ids':['AAAAAA'], 'serum_ids':['BBBBBB'], 'date':'now', 
           'file':'fake.csv', 'conducted_by':'Sina', 'assay':'HI', 'titers':[['1260']]}]
exp_list.create_entry('New result', 'Some fake new result', result)
exp_list.cross_check(antigen_list, serum_list)


try:
    exp_list.write(database_dir+'test_results3.json')
except ValueError as e:
    print(e)


# In[15]:


# lets add them and should work fine
antigen_list.create_entry('Antigen1','AAAAAA')
serum_list.create_entry('Serum1', 'BBBBBB')
exp_list.cross_check(antigen_list, serum_list)
exp_list.write(database_dir+'test_results3.json')


# In[16]:


# cross-check can also fail if antigen and serum lists are not correct
# for instance if a serum or antigen id in the experiment appears twice
# in serum or antigen lists.

# lets try to defile the antigen list 
try:
    antigen_list.create_entry('Maybe new Antigen?','AAAAAA')
except AssertionError as e:
    print(e)
    


# In[17]:


# need to turn checks off
antigen_list._check_new_entries = False
antigen_list.create_entry('Maybe new Antigen?','AAAAAA')

# now lets try cross-check and see that the antigen appears multiple times
exp_list.cross_check(antigen_list, serum_list)
try:
    exp_list.write(database_dir+'test_results3.json')
except ValueError as e:
    print(e)

antigen_list.pop(-1)
exp_list.cross_check(antigen_list, serum_list)
try:
    exp_list.write(database_dir+'test_results3.json')
except ValueError as e:
    print(e)
