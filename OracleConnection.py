import cx_Oracle 
import numpy as np   
from tkinter import *
from functools import partial, partialmethod

class DBUI:
    
    def __init__(self, user, password, DBname):
        self.connection = cx_Oracle.connect(user, password, DBname, encoding = "UTF-8")
        self.cursor = None
        self.win = Tk()
        self.frames = {}
        self.widgets = {}
        self.viewCommands = {}
        
        self.debug = True

        
        self.active_table = ''
        self.view_id = ''
        self.view_name = ''
        
        
        self.elementEnter = Entry(self.win, width = 30)
        self.elementEnter.grid(column = 0, row = 0)
        
        
        remove_action = partial(self.Remove, self.active_table, self.view_id)
        
        self.removeBut = Button(self.win, text = 'Remove', command = lambda: self.Remove(self.active_table, self.view_id))
        self.removeBut.grid(column = 2, row = 0)
        
        
        add_action = partial(self.Add,self.elementEnter.get())
        
        self.addBut = Button(self.win, text = 'Add', command = lambda:self.Add(self.elementEnter.get()))
        self.addBut.grid(column = 1, row = 0)
        
        self.nameLabel = Label(self.win)
        self.nameLabel.grid(column = 0, row = 1)
        
        
        self.list = Listbox(self.win, width = 30, height = 20)
        self.list.grid(column = 0, row = 2)
        
        self.list.bind("<<ListboxSelect>>",self.OnSelect )
        
        
        self.info_frame = Frame(self.win)
        
        
        
        self.updatingEntry = Entry(self.info_frame, width = 10)
        self.updatingEntry.bind("<Return>",self.OnSubmitUpdate)
        
        self.buffAtribute = ''
        self.buffElement = ''
        
        
        
        self.active_table_types = None
        self.active_table_ids = None
        self.active_table_columns = None
        self.active_table_nullable = None
        self.buffData = None
        
        self.info_labels = []
        for i in range(3):
            for j in range(2):
                
                
                self.info_labels.append(Label(self.info_frame))
                self.info_labels[-1].grid(column = i, row = j)
                self.info_labels[-1].bind("<Button-1>", partial(self.GetForUpdate, label = self.info_labels[-1], index = len(self.info_labels)-1))
        
        self.updating_label = None
        
        
        self.active_table_references = None
        
        self.mainmenu = Menu(self.win) 
        self.win.config(menu=self.mainmenu)
    def GetValueByType(self, value, type, in_command = False):
        if type == 'NUMBER':
            return int(value)
        elif type == 'VARCHAR' or type == 'VARCHAR2':
            if in_command:
                return "'{0}'".format(value)
            return "{0}".format(value)
        elif type == 'DATE':
            return "to_date('{0}','dd-mm-yyyy')".format(value)
        return value
    def OnSubmitUpdate(self,event):
        self.cursor = self.connection.cursor()
        
        
        
        try:
            value = self.updatingEntry.get()
            
            
            print(self.active_table_types,self.buffData, self.buffAtribute)
            in_data = self.GetValueByType(value, self.buffData, in_command = True)
            
            
            out_data = self.GetValueByType(self.buffElement, self.active_table_types[np.where(self.active_table_columns == self.view_name.upper())], in_command = True) 
            command = 'update {0} set {1} = {2} where {3} = {4}'.format(self.active_table.upper(), self.buffAtribute.upper(), in_data, self.view_name.upper(), out_data)
            
            print(command)
            self.cursor.execute(command)
            
        except Exception as e:
            messagebox.showerror(title = 'error on submit', message = e)
            print(e)
            grid_info = self.updatingEntry.grid_info()
            self.updatingEntry.delete(0, END)
            self.updatingEntry.grid_forget()
            self.updating_label.grid(column = grid_info['column'], row = grid_info['row'])
            self.updating_label = None
            self.cursor.close()
        else:
            print('ok')
            name_changing = False
            new_value = None
            list_index = 0
            grid_info = self.updatingEntry.grid_info()
            if self.buffAtribute.upper() == self.view_name.upper():
                name_changing = True
                new_value = self.updatingEntry.get()
                list_index = self.list.get(0, END).index(self.buffElement)
                
                #self.list.get( )
            self.updating_label['text'] = self.buffAtribute + ': ' + self.updatingEntry.get()
            self.updatingEntry.grid_forget()
            self.updating_label.grid(column = grid_info['column'], row = grid_info['row'])
            self.updating_label = None
            self.updatingEntry.delete(0, END)
            
            if name_changing:
                self.list.delete(list_index)
                self.list.insert(list_index,new_value)
                self.list.select_set(list_index)
                self.cursor.close()
                self.OnSelect('custom_call')
            else:
                self.cursor.close()
        
    def OnSelect(self,event):
        self.cursor = self.connection.cursor()
        if self.updating_label!=None:
            grid_info = self.updatingEntry.grid_info()
            self.updatingEntry.delete(0,END)
            self.updatingEntry.grid_forget()
            self.updating_label.grid(column = grid_info['column'], row = grid_info['row'])
            self.updating_label = None
        try:
            command = "select * from {0} where {1} = '{2}'".format(self.active_table.upper(), self.view_name, self.list.get(self.list.curselection()))
            self.buffElement = self.list.get(self.list.curselection())
            element_info = np.array(self.cursor.execute(command).fetchone())
            
            
            
            if element_info.shape != self.active_table_columns.shape:
                element_info = np.array([None]*self.active_table_columns.shape[0])
            
            
            for i in range(self.active_table_ids.shape[0]):
                self.info_labels[i].config(text = str(self.active_table_columns[i]) + ": " + str(element_info[i]))
            self.info_frame.grid(column = 1, row = 2)
            
        except Exception as e:
            messagebox.showerror(title = 'error on selection', message = e)
            print(e, ' On Select')
        self.cursor.close()
    def GetForUpdate(self, event, label: Label, index):
        
        
        if not label.cget("text") == '':
            if self.updating_label!=None:
                grid_info = self.updatingEntry.grid_info()
                self.updatingEntry.grid_forget()
                self.updating_label.grid(column = grid_info['column'], row = grid_info['row'])
                self.updating_label.config(text = self.buffAtribute + ': ' + self.updatingEntry.get())    
                
            self.updating_label = label
            
            grid_info = self.updating_label.grid_info()
            self.updating_label.grid_forget()
            self.updatingEntry.grid(column = grid_info['column'], row = grid_info['row'])
            self.updatingEntry.delete(0,END)
            
            attribute, value = tuple(self.updating_label['text'].split(': '))
            self.buffAtribute = attribute
            self.updatingEntry.insert(0,value)
           
            self.buffData = self.active_table_types[index]
            
            #self.updating_label.config(bg="green")
            #grid_info = self.updating_label.grid_info()
            #TODO: при нажатии вместо надписи появляется место ввода, где записано текущее значение, после нажатия enter все меняется
    def SetMenu(self, tables, view_name, view_ids):
        self.tablesmenu = Menu(self.mainmenu, tearoff=0)
        for i in range(len(tables)):
            action_ = partial(self.ChangeTable,tables[i], view_name[i], view_ids[i])
            self.tablesmenu.add_command(label = tables[i], command = action_ )
        self.mainmenu.add_cascade(label="Таблици", menu=self.tablesmenu)
        self.ChangeTable(tables[0], view_name[0], view_ids[0])
    def Update(self):
        self.win.mainloop()
    def Close(self):
        if self.debug:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()  
    def ChangeTable(self, table, view_name, view_id):
        self.cursor = self.connection.cursor()
        self.active_table = table 
        self.view_id = view_id
        self.view_name = view_name
        self.info_frame.grid_forget()
        self.buffElement = ""
        
        self.nameLabel.config(text = table)
        if self.updating_label!=None:
            grid_info = self.updatingEntry.grid_info()
            self.updatingEntry.delete(0,END)
            self.updatingEntry.grid_forget()
            self.updating_label.grid(column = grid_info['column'], row = grid_info['row'])
            self.updating_label = None
        
        for i in self.info_labels:
            i['text'] = ''
            
            
            
            
        self.active_table_ids = np.array(self.cursor.execute("select column_id from ALL_TAB_COLUMNS  where TABLE_NAME = UPPER('{0}')".format(table)).fetchall())
        self.active_table_ids = self.active_table_ids[:,0].astype(int) - 1
        
        
        indexes = np.argsort(self.active_table_ids)
        
        self.active_table_types = np.array(self.cursor.execute("select data_type from ALL_TAB_COLUMNS  where TABLE_NAME = UPPER('{0}')".format(table)).fetchall())
        self.active_table_types = self.active_table_types[:,0]
        
        self.active_table_types = self.active_table_types[indexes]
        
        self.active_table_columns = np.array(self.cursor.execute("select column_name from ALL_TAB_COLUMNS  where TABLE_NAME = UPPER('{0}')".format(table)).fetchall())
        self.active_table_columns = self.active_table_columns[:,0]
        
        self.active_table_columns = self.active_table_columns[indexes]
                                                              
        self.active_table_nullable = np.array(self.cursor.execute("select nullable from ALL_TAB_COLUMNS  where TABLE_NAME = UPPER('{0}')".format(table)).fetchall())
        self.active_table_nullable = self.active_table_nullable[:,0]
        
        self.active_table_nullable = self.active_table_nullable[indexes]                                                 
        
        
        
        #command = "select TABLE_NAME, ORIGIN_CON_ID from user_constraints where constraint_name in (select r_constraint_name from user_constraints where table_name = UPPER('{0}') and constraint_type = 'R')".format(self.active_table)
        
        #self.active_table_references = np.array(self.cursor.execute(command).fetchall())
        #print(self.active_table_references)
        names = np.array(self.cursor.execute('select {0} from {1}'.format(view_name, table)).fetchall())
        
        self.list.delete(0, self.list.size())
       # self.infoLabel.config(text = '')
        for i in names:
            self.list.insert(self.list.size(), i[0])
        self.cursor.close()
            
    
    
    
    def Add(self, value):
        
        table = self.active_table
        index = np.where(self.active_table_columns == self.view_name.upper())[0][0]
        value = self.GetValueByType(value, self.active_table_types[index])
        print(self.active_table_types[index],value)
        
        self.cursor = self.connection.cursor() 
        try:
            
            
            #info_handler = np.array(self.cursor.execute('select column_name, data_type,nullable , column_id from ALL_TAB_COLUMNS where TABLE_NAME = %s' % ("'"+table.upper()+"'")).fetchall())
            #column_names = info_handler[:,0]
            #data_types = info_handler[:,1]
            #nullable = info_handler[:,2]
            #column_ids = info_handler[:,3].astype(int) -1
            
            
            column_names = self.active_table_columns
            data_types = self.active_table_types
            nullable = self.active_table_nullable
            column_ids = self.active_table_ids
            
            count = self.active_table_columns.shape[0]
            index = np.where(column_names == self.view_name.upper())[0][0]
            print(index)
            values = np.array([None]*count)
            
            value_inserted = False
            
            for n,i in enumerate(data_types):    
                n = column_ids[n]
                if n == index:
                        values[n] = value
                        value_inserted = True
                        #values += (value,)
                else:
                    if nullable[n] == 'N':
                        if n == index:
                            values[n] = value
                            value_inserted = True
                            #values += (value,)
                        elif i == 'NUMBER':
                            if column_names[n] == self.view_id.upper():
                                values[n] = self.cursor.execute('select {0}.nextval from dual'.format((table+'_seq').upper())).fetchone()[0]
                            else:
                                values[n] = 0
                                #values += (0,)
                        elif i == 'VARCHAR' or i == 'VARCHAR2':
                            values[n] = 'nothing here'
                            #values += ('nothing here',)
                        elif i == 'DATE':
                            date = self.cursor.execute("SELECT TO_CHAR(SYSDATE, 'MM-DD-YYYY') FROM DUAL").fetchone()[0]
                            values[n] = date
                            #values += (date,)
            
            value_str = str(tuple(values)).replace('None', 'NULL')
                
            if not value_inserted:
                raise Exception('value doestn`t inserted')
            
            command = 'insert into {0} values {1}'.format(table.upper(), value_str)
            print(command)
            self.cursor.execute(command)
        except Exception as e:
            messagebox.showerror(title = 'error on add', message = e)
            print('cant add')
            print(e)
        else:
            self.list.insert(self.list.size(),value)
        
        self.cursor.close()
    def Remove(self, table, view_id):
        self.cursor = self.connection.cursor()
        index = 0
        try:
            index = self.list.index(self.list.curselection())
            self.cursor.execute('delete from {0} where {1} = {2}'.format(table, view_id, index))
            self.info_frame.grid_forget()
            self.buffElement = ""
            self.updating_label = None
        except Exception as e:
            messagebox.showerror(title = 'error on delete', message = e)
            print('cant delete')
            print(e)
        else:
            self.list.delete(index,index)
        self.cursor.close()
    
if __name__ == "__main__":
    
    view_name = ['country_name', 'object_name', 'object_id', 'class_name', 'category_name', 'continent_name', 'creation_type_name', 'coords', 'climate_type', 'weather']
    view_ids = ['country_id', 'object_id', 'object_id', 'class_id', 'category_id', 'continent_id', 'creation_type_id', 'location_id', 'climate_id', 'weather_id']
    tables = ['countries', 'objects', 'histories','objectclasses','categories','continents','creationtypes','locations','climates','weathers']

    data = DBUI("c##vadim",'vp','ORCL')
    data.SetMenu(tables, view_name, view_ids)   
    
 
    data.Update()
    data.Close()

# берем 


