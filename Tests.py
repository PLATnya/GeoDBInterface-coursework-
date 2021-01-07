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
   # @unittest.skip('no reason')
    def test_rollback(self):
        
        
        res = np.array(self.cursor.execute("select column_name, data_type, column_id from ALL_TAB_COLUMNS where TABLE_NAME = 'HISTORIES'").fetchall())
        indexes = np.argsort(res[:,2].astype(int) - 1)
        
        #values = np.array([res[:,0][i] for i in np.argsort(indexes)])
        print(res[:,0][indexes])
        
        self.cursor.execute("insert into HISTORIES values(to_date('12.04.2002','dd-mm-yyyy'),'sdfsdf',3)")
        self.cursor.close()
        self.connection.rollback()
        self.connection.close()
        self.assertEqual(5, 5)
    @unittest.skip('no reason')
    def test_commit(self):
        self.cursor.close()
        #self.connection.commit()
        self.connection.close()
        self.assertEqual(True,True)

if __name__ == "__main__":
    unittest.main()
    
    