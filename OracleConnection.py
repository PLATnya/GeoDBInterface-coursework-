# несколько страниц
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
        
        self.list = Listbox(self.win, width = 30, height = 20)
        self.list.grid(column = 0, row = 1)
        
        self.list.bind("<<ListboxSelect>>",self.OnSelect )
        
        
        self.info_frame = Frame(self.win)
        self.info_frame.grid(column = 1, row = 1)
        self.info_labels = []
        for i in range(3):
            for j in range(2):
                
                
                self.info_labels.append(Label(self.info_frame))
                self.info_labels[-1].grid(column = i, row = j)
                self.info_labels[-1].bind("<Button-1>", partial(self.GetForUpdate, label = self.info_labels[-1]))
                '''
                label = Label(self.info_frame, name = str(i*2 + j))
                label.grid(column = i, row = j)
                
                self.info_labels.append(label)'''
        #self.infoLabel = Label(self.win, text = 'fuck')
        #self.infoLabel.bind("<Button-1>", lambda e:print('sdff'))
        #self.infoLabel.grid(column = 1, row = 1)
        
        
        self.updating_label = None
        
        self.mainmenu = Menu(self.win) 
        self.win.config(menu=self.mainmenu)
        
    
    def OnSelect(self,event):
        self.cursor = self.connection.cursor()
        try:
            command = "select * from {0} where {1} = '{2}'".format(self.active_table.upper(), self.view_name, self.list.get(self.list.curselection()))
            element_info = np.array(self.cursor.execute(command).fetchone())
            column_names = np.array(self.cursor.execute('select column_name from ALL_TAB_COLUMNS where TABLE_NAME = %s' % ("'"+self.active_table.upper()+"'")).fetchall())
            column_names = column_names[::-1]
            for i in range(element_info.shape[0]):
                self.info_labels[i].config(text = str(column_names[i]) + ": " + str(element_info[i]))
        except Exception as e:
            print(e)
        self.cursor.close()
    def GetForUpdate(self, event, label):
        
        
        print(label["text"])
        if not label.cget("text") == '':
            if self.updating_label!=None:
               self.updating_label.config(bg="white")
            self.updating_label = label
            self.updating_label.config(bg="green")

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
    def AddFrame(self,name):
        self.frames[name] = Frame(self.win)
        self.widgets[name] = {}
    def ChangeFrame(self,name):
        self.frames[self.active_frame].grid_forget()
        
        
        
        #self.frames[name].grid(column = 0,row = 0)
        self.active_frame = name
    def AddButton(self, name,frame,text, command, column = 0, row = 0):
        self.widgets[frame][name] = Button(self.frames[frame],text = text,command = command)
        self.widgets[frame][name].grid(column = column, row = row)
    def AddLabel(self, name, frame, text, column, row):
        self.widgets[frame][name] = Label(self.frames[frame],text = text)
        self.widgets[frame][name].grid(column = column, row = row)
    def AddBox(self,name,frame, width, height, column, row):
        self.widgets[frame][name] = Listbox(self.frames[frame], width = width, height = height)
        self.widgets[frame][name].grid(column = column, row = row)
    def UpdateDB(self, command):
        self.cursor = self.connection.cursor()
        res = np.array(self.cursor.execute(command).fetchall())
        names = np.array(self.cursor.description)[:,0]
        self.cursor.close()
        
        
    def ChangeTable(self, table, view_name, view_id):
        self.cursor = self.connection.cursor()
        self.active_table = table 
        self.view_id = view_id
        self.view_name = view_name
        
        
        
        
        names = np.array(self.cursor.execute('select {0} from {1}'.format(view_name, table)).fetchall())
        
        self.list.delete(0, self.list.size())
       # self.infoLabel.config(text = '')
        for i in names:
            self.list.insert(self.list.size(), i)
        self.cursor.close()
            
        
    def Add(self, value):
        table = self.active_table
        self.cursor = self.connection.cursor() 
        try:
            info_handler = np.array(self.cursor.execute('select column_name, data_type, nullable from ALL_TAB_COLUMNS where TABLE_NAME = %s' % ("'"+table.upper()+"'")).fetchall())
            column_names = info_handler[:,0]
            data_types = info_handler[:,1]
            nullable = info_handler[:,2]
            
            count = column_names.shape[0]
            index = np.where(column_names == self.view_name.upper())[0][0]
              
            values = ()
            for n,i in enumerate(data_types):    
                  
                if n == index:
                    values += (value,)
                elif column_names[n] == self.view_id.upper():
                    values += self.cursor.execute('select {0}.nextval from dual'.format((table+'_seq').upper())).fetchall()[0]
                elif nullable[n] == 'Y':
                    values += (None,)
                elif nullable[n] == 'N':
                    if i == 'NUMBER':
                        values += (0,)
                    elif i == 'VARCHAR' or i == 'VARCHAR2':
                        values += ('nothing',)
    
                      
            values = values[::-1]
            value_str = str(values).replace('None', 'NULL')
              
            self.cursor.execute('insert into {0} values {1}'.format(table.upper(), value_str))
        except Exception as e:
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
        except Exception as e:
            print('cant delete')
            print(e)
        else:
            self.list.delete(index,index)
        self.cursor.close()
    
if __name__ == "__main__":
    
    view_name = ['object_name', 'country_name', 'category_name']
    view_ids = ['object_id', 'country_id', 'category_id']
    tables = ['Objects', 'Countries', 'Categories']

    data = DBUI("c##vadim",'vp','ORCL')
    data.SetMenu(tables, view_name, view_ids)   
    
 
    data.Update()
    data.Close()




