import tkinter as tk
from tkinter import Menu
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox as mBox
from utils.mongodb import Stations

class OOP():

    def __init__(self):
        self.win = tk.Tk()
        self.win.title('NCDC Weather Stations')
        self.createWidgets()
        self.db_conn = Stations()

    def _quit(self):
        self.win.quit()
        self.win.destroy()
        exit()


    def _aboutMsgBox(self):
        mBox.showinfo('Weather Stations',
                      'GUI to show NCDC weather station information.\nJohn Kinder - 2019')


    def _usageMsgBox(self):
        mBox.showinfo('Usage',
                      'Provide a latitude and / or longitude - integer part only.\n' +
                      'Provide a plus/minus range.\nOmitting +/- checks only within the integer part.\n' +
                      '\nBoth latitude and longitude cannot be blank.')


    def _searchMsgBox(self, msg):
        mBox.showerror('Error', msg)



    def searchBtnClick(self):
        '''Check our values in the text boxes and print results.'''
        lat = self.latValue.get()
        lon = self.lonValue.get()
        latpm = self.latPMValue.get()
        lonpm = self.lonPMValue.get()
        # one of the two must be provided
        if lat == '' and lon == '':
            msg = 'At least one must be provided: latitude or longitude'
            self._searchMsgBox(msg)
            return

        # If lat was not empty str, make sure it is an integer
        if lat != '':
            try:
                lat = int(lat)
            except ValueError:
                msg = 'Latitude cannot be converted to an integer: {}'.format(lat)
                self._searchMsgBox(msg)
                self.latValue.set('')
                return

        # If lon was not empty str, make sure it is an integer
        if lon != '':
            try:
                lon = int(lon)
            except ValueError:
                msg = 'Longitude cannot be converted to an integer: {}'.format(lon)
                self._searchMsgBox(msg)
                self.lonValue.set('')
                return

        # Variables are valid. Clear ScrolledText.
        self.resultText.delete('1.0', tk.END)

        # Send request to the mongo class Stations
        results = self.db_conn.get_locations(lat, latpm, lon,lonpm)

        # Stations will return None if results were empty.
        if results == None:
            self.resultText.insert(tk.INSERT, 'No results found.')
        else:
            for result in results:
                self.resultText.insert(tk.INSERT, '{:20}{:30}{:<15.3f}{:15.3f}\n'.format(
                    result.get('station_id'), result.get('name'),
                    result.get('lat'), result.get('lon'))
                )




    def createWidgets(self):
        # Menu Bar setup
        menuBar = Menu(self.win)
        self.win.config(menu=menuBar)
        # file menu
        fileMenu = Menu(menuBar)
        fileMenu.add_command(label='Exit', command=self._quit)
        menuBar.add_cascade(label='File', menu=fileMenu)
        # help menu
        helpMenu = Menu(menuBar)
        helpMenu.add_command(label='Usage', command=self._usageMsgBox)
        helpMenu.add_command(label='About', command=self._aboutMsgBox)
        menuBar.add_cascade(label='Help', menu=helpMenu)

        # top level labels
        latLabel = ttk.Label(self.win, text='Latitude')
        latLabel.grid(column=0, row=0, pady=5)
        latPMLable = ttk.Label(self.win, text='+/-')
        latPMLable.grid(column=1, row=0, pady=5)

        lonLabel = ttk.Label(self.win, text='Longitude')
        lonLabel.grid(column=2, row=0, pady=5)
        lonPMLable = ttk.Label(self.win, text='+/-')
        lonPMLable.grid(column=3, row=0, pady=5)

        # add text fields and variables
        # set all to blank
        self.latValue = tk.StringVar()
        self.latValue.set('')
        self.latPMValue = tk.IntVar()
        self.lonValue = tk.StringVar()
        self.lonValue.set('')
        self.lonPMValue = tk.IntVar()

        latTextField = ttk.Entry(self.win, width=20, textvariable=self.latValue)
        latPMIntField = ttk.Entry(self.win, width=3, textvariable=self.latPMValue)
        latTextField.grid(column=0, row=1, pady=5)
        latPMIntField.grid(column=1, row=1, pady=5)

        lonTextField = ttk.Entry(self.win, width=20, textvariable=self.lonValue)
        lonPMIntField = ttk.Entry(self.win, width=3, textvariable=self.lonPMValue)
        lonTextField.grid(column=2, row=1, pady=5)
        lonPMIntField.grid(column=3, row=1, pady=5)

        # search button
        action = ttk.Button(self.win, text='Search', command=self.searchBtnClick)
        action.grid(columnspan=4, row=2, pady=5, padx=5, sticky='nesw')

        # labels for text area
        idLabel = ttk.Label(self.win, text='Station ID')
        nameLabel = ttk.Label(self.win, text='Station Name')
        retLatLabel = ttk.Label(self.win, text='Latitude')
        retLonLabel = ttk.Label(self.win, text='Longitude')
        idLabel.grid(column=0, row=3, pady=5, padx=5, sticky='w')
        nameLabel.grid(column=1, row=3, pady=5)
        retLatLabel.grid(column=2, row=3, pady=5)
        retLonLabel.grid(column=3, row=3, pady=5)

        # finally the ScrollableText area for results
        self.resultText = scrolledtext.ScrolledText(self.win, width=80, height=20)
        self.resultText.grid(column=0, columnspan=4, pady=5)

oop= OOP()
oop.win.mainloop()