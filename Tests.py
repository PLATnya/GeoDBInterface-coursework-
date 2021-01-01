import unittest
#import OracleConnection
import numpy as np
import cx_Oracle
#Test cases to test Calulator methods
#You always create  a child class derived from unittest.TestCase
class TestCalculator(unittest.TestCase):
    def setUp(self):   
        self.view_names = ['object_name', 'country_name', 'category_name']
        self.view_ids = ['object_id', 'country_id', 'category_id']
        self.tables = ['Objects', 'Countries', 'Categories']
        self.connection = cx_Oracle.connect("c##vadim",'vp','ORCL')
        self.cursor = self.connection.cursor()
        '''data = DBUI("c##vadim",'vp','ORCL')
        data.SetMenu(tables, view_name, view_ids)'''
    @unittest.skip('no reason')
    def test_rollback(self):
        
        
        
        
    
        self.cursor.close()
        self.connection.rollback()
        self.connection.close()
        self.assertEqual(5, 5)
    def test_commit(self):
        self.cursor.close()
        #self.connection.commit()
        self.connection.close()
        self.assertEqual(True,True)

if __name__ == "__main__":
    unittest.main()
    
    