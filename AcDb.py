#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 16:32:46 2021

@author: iavicenna
"""


import json
import collections
import uuid
import numpy as np
import logging
MAPTYPES = (dict, collections.abc.Mapping)
KNOWN_TITER_SYMBOLS = ['<', '>', '/', '*', ' ', '?']
REQUIRED_EXP_KEYS = ['titers', 'antigen_ids', 'serum_ids', 'assay', 'file', 'conducted_by']

class db_list(list):
    '''
    This is the base parent class for db_antigen_list, db_serum_list, db_experiment_list
    which are esentially lists with some extra functionality such as adding items need
    to pass some checks and some control such as setting is not allowed.
    
    Insert and append are only defined for child classes since each child class will have
    its own rules on insert and append
    
    If you want you can provide a name for your list for convenience
        
    '''
    
    def __init__(self, json_path, name=None, do_tests=True):
        
        assert isinstance(json_path,str)
        
        with open(json_path, 'r') as fileobj:
            self._list = json.load(fileobj)
        
        assert len(self._list)>0, 'list contains no elements'    
        
        
        if name is None:
            name = ''
            
        self.name = name
            
        self._id_list = [x['id'] for x in self._list]
        
        self._check_new_entries = True  #  WARNING: turn off at your own expense. 
                                    #  This is a check used when adding new entries
    
        self._do_tests = do_tests  #  WARNING: turn off at your own expense. 
                               #  This is for testing the lists when loading them
                               
        if self._do_tests:
            self._parent_tests()
    
    def __repr__(self):
        return "<{0} {1}>".format(
            self.__class__.__name__, self._list)

    def __len__(self):
        """List length"""
        return len(self._list)
    
    def __setitem__(self, val, ii):
        
        raise TypeError(f'Setting values not allowed for {self.__class__.__name__}')

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __delitem__(self, ii):
        self._list.__delitem__(ii)
        self._id_list__delitem__(ii)
        
    def __str__(self):
        return ''.join([str(x) + '\n' for x in self._list])
    
    def __iter__(self):
        return iter(self._list)
    
    def _test(self):
        assert len(self._id_list) == len(set(self._id_list)), 'Non-uniqueness in the ids'
        
    def insert(self,ii,val):
        raise TypeError(f'Insert is only defined for child classes of {self.__class__.__name__}')
    
    def append(self, val):
        raise TypeError(f'Append is only defined for child classes of {self.__class__.__name__}')

        
    def pop(self, ii):
        self._list.pop(ii)
        self._id_list.pop(ii)
        
    def reverse(self):
        self._list.reverse()
        self._id_list.reverse()

    def generate_new_id(self, stop=10000):
        
        is_unique = False
        counter = 0
        
        while not is_unique:
            random_id = str(uuid.uuid4())
        
            random_id = random_id.upper()
        
            random_id = random_id.replace("-","")
            
            counter +=1 
            
            if random_id not in self._id_list:
                is_unique=True
                
            elif counter>stop:
                assert f'Unique id could not be produced after {stop} steps, check your inputs'
            
    
        return random_id[0:6]
 
    
 
    def write(self, path):
    
        '''a save json function which is compatible
        with the formatting of our datasets. This is overwritten
        slightly in db_experiment_list for some extra functionality
        '''
        
        json_data = self._list
        
        with open(path, "w") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            json_file.write("\n")  # Add newline at the end of the last line 
            json_file.write("\n")  # Add newline after the json data   
 
    def _parent_tests(self):
        
        assert isinstance(self._list, list) and all(isinstance(x, dict) for x in self._list), 'provide a json file which is a list of dictionaries'
    
        assert len(self._id_list) == len(set(self._id_list)), 'Some ids appear multiple times'
 
class db_experiment_list(db_list):
    
    '''
    This inherits from db_list and adds insert, append, create_entry
    functionalities. The reason why these are child dependant functions is
    during these some checks are made to make sure the entries that you are trying
    to add to the list have the format required by experiment datasets in our database.
    '''

    def __init__(self, json_path, name=None):  

        super().__init__(json_path, name)
        
        # these are used during writing the list to a file
        self._cross_check_complete = False
        self._cross_check_failed = False
        self._cross_check_required = True
        
        if self._do_tests:
            self._test()
        
    def insert(self, ii, val):
        
        if self._check_new_entries:
            self._check_entry(val)
        
        self._id_list.insert(ii, val['id'])
        self._list.insert(ii, val)
        
    def append(self, val):
        
        self.insert(len(self._list), val)

    def create_entry(self, ename, edesc, eresults, eid=None):
        
        if eid is not None:
            assert len(eid)==6 and all(x.isalnum() for x in eid),'entry id should be alpha numerical of length 6'
            assert eid not in self._id_list, 'entry should not already exist in the list'
        else:
            eid = self.generate_new_id()
        
        assert isinstance(ename,str) and len(ename)>0, 'entry name should be a non-empty string'
        assert isinstance(edesc,str) and len(edesc)>0, 'entry description should be a non-empty string'
        assert isinstance(eresults, list) and len(eresults) >0, 'entry results should be a non-empty list'
        
        entry = {}
        entry['id'] = eid
        entry['name'] = ename
        entry['description'] = edesc
        entry['results'] = eresults
        
        self.append(entry)
        
    def _test(self):
        
        for entry in self._list:
            try:
                self._check_result(entry)
            except AssertionError as e:
                raise AssertionError (f'Testing the existing data has failed with message: \n {e}')
    
        
    def _check_entry(self, val):
        
        assert isinstance(val, dict), f'value to be inserted should be a dictionary but is a {type(val)}'
        assert 'id' in val and all(x.isalnum() for x in val['id']) and len(val['id']) == 6, 'the dictionary should have an id field which is alphanumerical of length 6'
        
        val_id = val['id']
        
        if val_id in self._id_list:
            raise ValueError(f'an entry with the same id {val_id} already exists in the database (entry {self._id_list.index(val_id)})')
            
        self._check_result(val)
            
    def _check_result(self, val):
        
        '''
        this is a function which checks the results field of an experiment entry
        '''
        
        assert 'results' in val and len(val['results'])>0, 'experiment entry should contain a non-empty results field'
        assert all(isinstance(x,dict) for x in val['results']), 'all entries in results should be a dictionary'
        assert 'description' in val and len(val['description'])>0, 'experiment entry should contain description'
        assert 'name' in val and len(val['name'])>0, 'experiment entry should contain name'
        
        exp_name = val['name']
        
        for ind,result in enumerate(val['results']):
            log_result = f'result {ind} of experiment {exp_name}'
            
            for key in REQUIRED_EXP_KEYS:
                assert key in result, f'{key} does not exist in ' + log_result
            
            # check format of some critical fields 
            assert isinstance(result['serum_ids'], list) and all(isinstance(x,str) for x in result['serum_ids']), 'serum_ids in ' + log_result + 's hould be a list of strings'
            assert isinstance(result['antigen_ids'], list) and all(isinstance(x,str) for x in result['antigen_ids']), 'antigen_ids in ' + log_result + ' should be a list of strings'
            assert isinstance(result['titers'],list) and all(isinstance(x,list) for x in result['titers']), 'Titers in ' + log_result + ' should be a list of lists'
            assert all(isinstance(x,str) for titer in result['titers'] for x in titer), 'Titers in ' + log_result + ' should all be of string format.'
            
            # check consistency of titer format, and some size checks wr to
            # number of antigens and sera
            assert len(result['titers']) == len(result['antigen_ids']), 'titers in ' + log_result + ' should be a list with the same length as number of antigens'
            assert all(len(x) == len(result['serum_ids']) for x in result['titers']), 'each element of titers list in ' + log_result +' should have the same length as number of sera'
            assert all(all(all([x.isnumeric() or x in KNOWN_TITER_SYMBOLS for x in titer]) for titer in row) for row in result['titers']), 'some titers in ' + log_result + ' have unknown format'
    
    def cross_check(self, antigen_list, serum_list):
        
        '''
        This is a bunch of tests to make sure that the experiment list is compatible
        with a corresponding list of antigens and sera.
        '''
        self._cross_check_failed = False
        list_serum_ids = [x['id'] for x in serum_list]
        list_antigen_ids = [x['id'] for x in antigen_list]
        
        
        for entry in self._list:
            entry_name = entry['name']

            
            for ind,result in enumerate(entry['results']):
                result_serum_ids = result['serum_ids']
                result_antigen_ids = result['antigen_ids']

                log_result = f'result {ind} of experiment {entry_name}'
             
                
                # check existence and uniqueness
                I0 = np.argwhere([x not in list_serum_ids for x in result_serum_ids]).flatten()
                I1 = np.argwhere(np.array([list_serum_ids.count(x) for x in result_serum_ids])>1).flatten()
                if len(I0)>0:
                   
                    logging.warning(f'Sera {[result_serum_ids[x] for x in I0]} of ' + log_result + ' do not exist in serum_list')
                    self._cross_check_failed = True
                if len(I1)>0:
                    logging.warning(f'Sera {[result_serum_ids[x] for x in I1]} of ' + log_result + ' appear multiple times in serum_list')
                    self._cross_check_failed = True
                # check existence and uniqueness
                I0 = np.argwhere([x not in list_antigen_ids for x in result_antigen_ids]).flatten()
                I1 = np.argwhere(np.array([list_antigen_ids.count(x) for x in result_antigen_ids])>1).flatten()
                if len(I0)>0:
                    logging.warning(f'Antigens {[result_antigen_ids[x] for x in I0]} of ' + log_result + ' do not exist in antigen_list')
                    self._cross_check_failed = True
                    
                if len(I1)>0:
                    
                    logging.warning(f'Antigens {[result_antigen_ids[x] for x in I1]} of ' + log_result + ' appear multiple times in antigen_list')
                    self._cross_check_failed = True
        
        self._cross_check_complete = True
        
        if not self._cross_check_failed:
            print(f'Cross check of experiment list {self.name} succesful.')
        
    def write(self, path):
        
        if (self._cross_check_required and self._cross_check_complete and not self._cross_check_failed or
            not self._cross_check_required):
               
            json_data = self._list
    
            with open(path, "w") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
                json_file.write("\n")  # Add newline at the end of the last line 
                json_file.write("\n")  # Add newline after the json data   
        else:
            if self._cross_check_complete and self._cross_check_failed   : 
                 raise ValueError(f'Cross check for experiment list {self.name} has failed')
            elif not self._cross_check_complete:
                raise ValueError(f'Cross check for experiment list {self.name} not complete')
class db_anti_list(db_list):

    '''
    This datastructure is like for db_experiment_list
    but is for antibodies and antigens.
    '''    

    def __init__(self, json_path, name=None):  

        super().__init__(json_path, name)
        
       
    def insert(self, ii, val):
        
        if self._check_new_entries:
            self._check_entry(val)
        
        self._id_list.insert(ii, val['id'])
        self._list.insert(ii, val)
        
    def append(self, val):
        
        self.insert(len(self._list), val)   
        
    def _check_entry(self, val):
        
        assert isinstance(val, dict), 'value to be inserted should be a dictionary'
        assert 'id' in val and all(x.isalnum() for x in val['id']) and len(val['id']) == 6, 'the dictionary should have an id field which is alphanumerical of length 6'
        
        val_id = val['id']
        
        if val_id in self._id_list:
            raise ValueError(f'an entry with the same id {val_id} already exists in the database (entry {self._id_list.index(val_id)})')
            
    def create_entry(self, elong, eid=None):
        
            
        if eid is None:
            eid = self.generate_new_id()
        
        if self._check_new_entries:
            assert isinstance(elong,str) and len(elong)>0, 'entry long should be a non-empty string'
            assert len(eid)==6 and all(x.isalnum() for x in eid),'entry id should be alpha numerical of length 6'
            assert eid not in self._id_list, f'entry {eid} already exists in the list'
       
        entry = {}
        entry['id'] = eid
        entry['long'] = elong
       
        
        self.append(entry)
        
    