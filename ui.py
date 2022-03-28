# SQLite3 interface
# Project: CISP71 Fall/2020
#  Author: TuttiPazzo

import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.messagebox as msgbox
from database import *
from playsound import playsound
import random
import threading
from PIL import Image, ImageTk

dogDB = ""

class DataRecordForm(tk.Frame):
    md = 'playsound'
    """
    The input form for our widgets
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Keep track of input widgets
        self.inputs = {}
        self.txtEditLabels = {}
        self.db = ""
        self.selectedDog = ""
        self.frame = {}
        self.entryNames = ["Name", "Breed", "Age", "Color"]
        self.soundDir = "audio"
        self.soundList = ["dogwhine.wav", "Howl.wav", "pup1.wav", "pup2.wav", "pup4.wav", "pup5.wav", "pup6.wav", "pupwhimper.wav"]
        self.soundFirst = False

        # Load a gif
        self.frame["Image"] = tk.LabelFrame(self, text="")
        self.frame["Image"].grid(row=0, column=0)
        self.frameCnt = 9
        self.imageFrames = [PhotoImage(file='images/walkingdog.gif',format = 'gif -index %i' %(i)) for i in range(self.frameCnt)]
        self.imageLabel = ttk.Label(self.frame['Image'])
        self.imageLabel.grid(row=0,column=0, sticky=(tk.W + tk.E + tk.N))
        self.imageLabel.pack()
        self.frame["Image"].columnconfigure(0, weight=1)
        self.after(0, self.doImage, 0)

        # Build the dog information form
        self.dogInfoFrame = tk.LabelFrame(self, text="Dog Information")

        # Dog Information Form widgets
        c=0
        for col in self.entryNames:
            self.frame[col] = tk.Frame(self.dogInfoFrame)
            self.frame[col].grid(row=0, column=c)
            self.txtEditLabels[col] = ttk.Label(self.frame[col], text=col)
            self.txtEditLabels[col].grid(row=0,column=c, sticky=(tk.W + tk.E + tk.N))
            if col == "Age":
                self.inputs[col] = ttk.Combobox(self.frame[col], width=7)
                self.inputs[col]['values'] = list(range(30))
                self.inputs[col].current(0)
            else:
                self.inputs[col] = ttk.Entry(self.frame[col])

            self.inputs[col].grid(row=1, column=c, sticky=(tk.W + tk.E + tk.N))

            self.frame[col].columnconfigure(0, weight=1)
            c = c + 1
            
        self.dogInfoFrame.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # Dog List Form widgets
        self.dogListFrame = tk.LabelFrame(self, text="Dog List")

        # Create ScrollBar for TreeView
        self.verticalScrollBar = ttk.Scrollbar(self.dogListFrame, orient="vertical")
        self.verticalScrollBar.pack(side='right', fill='y')
        self.treeView = ttk.Treeview(self.dogListFrame,
                                     selectmode='browse',
                                     yscrollcommand=self.verticalScrollBar.set
                                    )
        self.treeView.pack(expand='True', fill=tk.X)
        self.treeView["columns"] = ("1", "2", "3", "4")
        self.treeView['show'] = 'headings'
        self.treeView.column("1", width=90, anchor='w')
        self.treeView.column("2", width=90, anchor='w')
        self.treeView.column("3", width=90, anchor='c', stretch='no')
        self.treeView.column("4", width=90, anchor='w')
        self.treeView.heading("1", text="Name")
        self.treeView.heading("2", text="Breed")
        self.treeView.heading("3", text="Age")
        self.treeView.heading("4", text="Color")
        self.treeView.bind("<<TreeviewSelect>>", self.showSelectedRecord)

        self.dogListFrame.grid(row=2, column=0, sticky="nsew")

        # Database Functions form
        self.dbFrame = tk.LabelFrame(self, text="Database Functions")

        self.createBtn = ttk.Button(self.dbFrame, text="Create", command=self.onCreate)
        self.createBtn.grid(sticky=tk.E, row=0, column=0, padx=10, pady=10)

        self.updateBtn = ttk.Button(self.dbFrame, text="Update", command=self.onUpdate)
        self.updateBtn.grid(sticky=tk.E, row=0, column=1, padx=10, pady=10)

        self.deleteBtn = ttk.Button(self.dbFrame, text="Delete", command=self.onDelete)
        self.deleteBtn.grid(sticky=tk.E, row=0, column=2, padx=10, pady=10)

        self.displayBtn = ttk.Button(self.dbFrame, text="Display All", command=self.onDisplayAll)
        self.displayBtn.grid(sticky=tk.E, row=0, column=3, padx=10, pady=10)

        self.dbFrame.grid(row=3, column=0, sticky=(tk.W + tk.E))

        self.after(2000, self.checkSoundMod)

    def doImage(self,index):
        frame = self.imageFrames[index]
        index += 1
        if index == self.frameCnt:
            index = 0
        self.imageLabel.configure(image=frame)
        self.after(100, self.doImage, index)

    def playDogSound(self, i):
        if i < len(self.soundList):
            playsound(self.soundDir + "/" + self.soundList[i])

    def doSound(self):
        if self.soundFirst == False:
            index = 1
            self.soundFirst = True
        else:
            index = random.randint(0, len(self.soundList))
 
        t = threading.Thread(target=self.playDogSound,args=[index])
        t.daemon = True    # kill thread if parent dies
        t.start()

        # self.after(random.randrange(5000, 10000), self.doSound())

    def checkSoundMod(self):
        if self.md not in sys.modules:
            self.msgBoxInfo("If you want to play sounds with this application, please include \"{0}\" module like so:\npip install {0}".format(self.md))

    def msgBoxInfo(self, msg):
        msgbox.showinfo("Info", msg)

    def checkData(self, data):
        msg = ""
        if bool(data) == False:
            msg = "Dog information info is empty.\nPlease enter values and try again."
        elif len(self.entryNames) != len(data):
            msg = "Dog information info is incomplete:"
        elif '' in data: 
            msg = "Dog information info is incomplete:"
        else:
            pass
    
        return msg


    def get(self):
        """
        Retrieve data from form as a list
        """
        data = []
        try:
            for key, widget in self.inputs.items():
                if key == "Age":
                    data.append(int(widget.get()))
                else:
                    data.append(widget.get())
        except ValueError as e:
            pass

        return data

    def set(self, key, val):
        """
        Set data for widget
        """
        self.inputs[key].delete(0, tk.END)
        self.inputs[key].insert(0, val)

    def reset(self):
        """
        Resets the form entries
        """
        # clear all values
        for key in self.inputs.keys():
            self.set(key,'')

    def showSelectedRecord(self, event):
        self.reset()
        selectedVals = []
        for selection in self.treeView.selection():
            item = self.treeView.item(selection)
            self.selectedDog = selection
            selectedVals = item["values"]

        if bool(selectedVals):
            i = 0
            for key in self.inputs.keys():
                self.set(key, selectedVals[i])
                i = i + 1

    def onCreate(self):
        """
        Handles create button clicks
        """
        data = self.get()
        msg = self.checkData(data)
        if msg != "":
            self.msgBoxInfo(msg)
            return

        # print(data)
        self.db.add(data)
        self.treeView.insert('', 'end', iid=None, values=data)
        self.doSound()

    def onUpdate(self):
        """
        Handles update button clicks
        """
        newData = self.get()
        data = self.get()
        msg = self.checkData(data)
        if msg != "":
            self.msgBoxInfo(msg)
            return
    
        oldData = []
        if( self.selectedDog ):
            item = self.treeView.item(self.selectedDog)
            oldData = item["values"]

        if( oldData == newData ):
            return

        if( oldData ):
            if( oldData == newData ):
                return

            self.db.update(oldData, newData)
            self.reset()
            self.onDisplayAll()
            self.doSound()

    def onDelete(self):
        """
        Handles delete button clicks
        """
        data = self.get()
        if (bool(self.selectedDog) == False) or len(data) == 0:
            self.msgBoxInfo("No item selected.\nPlease select an item from the list below & try again.")
            return

        msg = self.checkData(data)
        if msg != "":
            self.msgBoxInfo(msg)
            return
        self.treeView.delete(self.selectedDog)
        self.db.delete(data)
        self.reset()
        self.doSound()


    def onDisplayAll(self):
        """
        Handles Display All button clicks
        """
        self.reset()
        self.treeView.delete(*self.treeView.get_children())
        recs = self.db.getAllRows()
        for row in recs:
            self.treeView.insert('', 'end', iid=None, values=row)
        self.selectedDog = ""
        self.doSound()

class Application(tk.Tk):
    """
    Application root window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.winTitle = "Kennel Dogs"
        self.title(self.winTitle)
        self.resizable(width=False, height=False)
        self.recordform = DataRecordForm(self)
        self.recordform.grid(row=1, padx=10)

        # Populate the Dog list after 1 second
        # Have to do it this way because mainloop
        # hasn't been called yet
        self.after(1000, self.recordform.onDisplayAll)
        self.after(2000, self.recordform.checkSoundMod)

def dataBaseSetup():
    tableName = "Dogs"
    dbFile = "dogKennel.db"
    global dogDB
    createStmt = """CREATE TABLE IF NOT EXISTS {0} (
                            dName   TEXT,
                            dBreed  TEXT,
                            dAge    INTEGER,
                            dColor  TEXT);""".format(tableName)
    try:
        dogDB = database(tableName, createStmt, dbFile)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    dataBaseSetup()
    app = Application()
    app.recordform.db = dogDB
    app.mainloop()
