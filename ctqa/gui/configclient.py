import os, sys, json, platform
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from .. import confutil

import logging
from .. import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


class config_client:
  def __init__(self, parent, firstrun=False):
    self.parent = parent
    self.parent.configure(background='#ededed')
    self.firstrun = firstrun
    self.parent.resizable(width=False, height=False)
    if platform.system() == 'Darwin':
      self.parent.geometry('440x400')
    else:
      self.parent.geometry('350x400')
    self.parent.title('CTQA Service Configuration')
    try:
      img = tk.PhotoImage(file=resource_path('res/ctqa-icon.gif'))
      parent.tk.call('wm', 'iconphoto', parent._w, img)
    except tk.TclError:
      print("ERROR: Could not load ctqa-icon.gif from resources folder")

    # Setting up absolute locations
    self.location = os.path.abspath(os.path.dirname(sys.argv[0]))
    self.logpath = self.location + '/ctqa.log'
    self.confpath = self.location + '/config.json'
    self.reportspath = os.path.join(self.location, 'reports')

    # Loading config
    self.config = confutil.openConfig(self.confpath)

    # Placing components
    self.load_components()

    # Binding keyboard shortcuts
    # Ctrl-Shift-S => Save and Quit
    self.parent.bind('<Control-Shift-Key-S>', lambda event: self.save_and_quit())
  

  def load_components(self):
    #Attempt to reload config if we got a bad result
    if isinstance(self.config, int):
      self.config = confutil.openConfig(self.confpath)

    # Save and close buttons
    self.buttonframe = tk.Frame(self.parent, background='#ededed')
    self.savebutton = tk.Button(self.buttonframe, text='Save Configuration', width=20, state=tk.DISABLED, command=self.save_config, highlightbackground='#ededed')
    
    # Detecting if opened from client or first run
    if self.firstrun:
      self.closebutton = tk.Button(self.buttonframe, text='Next', width=10, command=self.exit_config, highlightbackground='#ededed')
    else:
      self.closebutton = tk.Button(self.buttonframe, text='Close', width=10, command=self.exit_config, highlightbackground='#ededed')
    self.savebutton.pack(side='left')
    self.closebutton.pack(side='right')
    self.buttonframe.pack(side='bottom', fill='x', padx=10, pady=(0,10))

    # Frame for config elements
    self.mainframe = tk.LabelFrame(self.parent, text='Options', background='#ededed')
    self.mainframe.pack(side='top', expand=True, fill='both', padx=10, pady=10)

    # Options components
    if isinstance(self.config, dict): #If the config is a dictionary (json)
      # Setting up source selection
      self.slabel = tk.Label(self.mainframe, text='Source:', background='#ededed')
      self.scombo = ttk.Combobox(self.mainframe, width=23, background='#ededed')
      self.scombo['values'] = confutil.SOURCE_LIST # Load list of a valid source options from confutil
      self.scombo['state'] = 'readonly'
      if self.config.get('Source') == '' or type(self.config.get('Source')) != str: # If the config has a bad value
        self.scombo.set('Select a data source...')
      else:
        self.scombo.set(self.config.get('Source'))
        self.load_source_components(self.config.get('Source')) # Load comps for that source value
      self.slabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(20,10))
      self.scombo.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(20,10))
      self.scombo.bind('<<ComboboxSelected>>', lambda event: self.component_change('Source', self.scombo.get())) # Save and update components on change

      # Setting up number of days to forecast
      self.fclabel = tk.Label(self.mainframe, text='Days to Forecast:', bg='#ededed')
      self.fcentry = tk.Entry(self.mainframe, width=25, justify=tk.RIGHT, highlightbackground='#ededed')
      self.fclabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(20,10))
      self.fcentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(20,10))
      self.fcentry.insert(0, self.config["DaysToForecast"])
      self.fcentry.bind("<KeyRelease>", lambda event: self.valid_days(self.fcentry.get(), "DaysToForecast"))

      # Setting up number of days for daily graphs
      self.gdlabel = tk.Label(self.mainframe, text='Days to Graph (Daily):', bg='#ededed')
      self.gdentry = tk.Entry(self.mainframe, width=25, justify=tk.RIGHT, highlightbackground='#ededed')
      self.gdlabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=(20,10))
      self.gdentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=(20,10))
      self.gdentry.insert(0, self.config["DailyReportDaysToGraph"])
      self.gdentry.bind("<KeyRelease>", lambda event: self.valid_days(self.gdentry.get(), "DailyReportDaysToGraph"))

      # Setting up number of days for weekly graphs
      self.wgdlabel = tk.Label(self.mainframe, text='Days to Graph (Weekly):', bg='#ededed')
      self.wgdentry = tk.Entry(self.mainframe, width=25, justify=tk.RIGHT, highlightbackground='#ededed')
      self.wgdlabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(20,10))
      self.wgdentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(20,10))
      self.wgdentry.insert(0, self.config["WeeklyReportDaysToGraph"])
      self.wgdentry.bind("<KeyRelease>", lambda event: self.valid_days(self.wgdentry.get(), "WeeklyReportDaysToGraph"))

      self.mainframe.grid_columnconfigure(0, weight=1)
      self.mainframe.grid_columnconfigure(1, weight=1)
      self.mainframe.grid_rowconfigure(0, weight=1)
      self.mainframe.grid_rowconfigure(1, weight=1)
      self.mainframe.grid_rowconfigure(2, weight=1)
      self.mainframe.grid_rowconfigure(3, weight=1)
      self.mainframe.grid_rowconfigure(4, weight=1)
    else:
      self.errMsg = tk.Label(self.mainframe, text='Error: Could not load config file.\n\n Would you like to generate a new one?')
      self.genConf = tk.Button(self.mainframe, text="Generate Config", width=20, command=self.generate_new_config)
      self.errMsg.grid(row=1, column=1, sticky='s')
      self.genConf.grid(row=2, column=1, sticky='n', pady=(10,0))

      self.mainframe.grid_rowconfigure(1, weight=1)
      self.mainframe.grid_rowconfigure(2, weight=1)
      self.mainframe.grid_columnconfigure(1, weight=1)
  

  def save_config(self):
    valid = confutil.validateConfig(self.config)
    if valid == 1:
      confutil.saveConfig(self.confpath, self.config)
      self.savebutton.configure(state=tk.DISABLED)
    else:
      self.parent.update()
      messagebox.showerror("Configuration Error", "There was a problem with the entered "+\
      "configuration values. \n\nPlease ensure they are correct and try to save again.", parent=self.parent)


  def exit_config(self):
    self.parent.destroy()


  def save_and_quit(self):
    self.save_config()
    self.exit_config()


  # NOTE: Any new sources must define an elif/function and place comps in self.scomps
  def load_source_components(self, src):
    if 'self.scomps' in locals(): # If scomps exists from before, we destroy it
      self.scomps.destroy()
    self.scomps = tk.Frame(self.mainframe, background='#ededed')
    self.scomps.grid(column=0, row=4, columnspan=2, rowspan=2, sticky='nsew')
    if src == 'TEST':
      return
    elif src == 'ORTHANC':
      self.load_orthanc_components()
      return


  def load_orthanc_components(self):
    # Orthanc address label
    self.orthiplabel = tk.Label(self.scomps, text='Orthanc REST Address:', background='#ededed')
    self.orthiplabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(0,10))

    # Create address entry and on validate, detect comp change
    self.orthip = tk.Entry(self.scomps, width=25, justify=tk.RIGHT)
    if self.config.get('OrthancRESTAddress') == '' or type(self.config.get('OrthancRESTAddress')) != str: # If the config has a bad value
      self.orthip.insert(0, 'Enter an address')
    else:
      self.orthip.insert(0, self.config.get('OrthancRESTAddress'))
    self.orthip.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(0,10))
    self.orthip.bind("<KeyRelease>", lambda event: self.component_change("OrthancRESTAddress", self.orthip.get()))

    self.scomps.grid_rowconfigure(0, weight=1)
    self.scomps.grid_rowconfigure(1, weight=1)
    self.scomps.grid_columnconfigure(0, weight=1)
    self.scomps.grid_columnconfigure(1, weight=1)

    #Image number label
    self.inumlabel = tk.Label(self.scomps, text='Last Image Number:', background='#ededed')
    self.inumlabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(0,10))

    # Create num entry and on validate, detect comp change
    self.inumentry = tk.Entry(self.scomps, width=25, justify=tk.RIGHT)
    if self.config.get('LastImageNumber') == '' or type(self.config.get('Source')) != str: # If the config has a bad value
      self.inumentry.insert(0, 'Enter a starting number')
    else:
      self.inumentry.insert(0, self.config.get('LastImageNumber'))
    self.inumentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(0,10))
    self.inumentry.bind("<KeyRelease>", lambda event: self.valid_image_number(self.inumentry.get()))


  def valid_image_number(self, num):
    if num == '':
      self.component_change("LastImageNumber", 0)
    else:
      try:
        num = int(num)
        self.component_change("LastImageNumber", num)
      except ValueError:
        self.inumentry.delete(0, 'end')
        if self.config.get('Last Image Number') == '' or type(self.config.get('Source')) != str: # If the config has a bad value
          self.inumentry.insert(0, 'Enter a starting number')
        else:
          self.inumentry.insert(0, self.config.get('LastImageNumber'))


  def valid_days(self, num, comp):
    if num == '':
      self.component_change(comp, 0)
    else:
      try:
        num = int(num)
        self.component_change(comp, num)
      except ValueError:
        if comp == "DaysToForecast":
          self.fcentry.delete(0, tk.END)
          self.fcentry.insert(0, self.config.get(comp))
        elif comp == "DailyReportDaysToGraph":
          self.gdentry.delete(0, tk.END)
          self.gdentry.insert(0, self.config.get(comp))
        elif comp == "WeeklyReportDaysToGraph":
          self.wgdentry.delete(0, tk.END)
          self.wgdentry.insert(0, self.config.get(comp))


  def component_change(self, name, value):
    self.config[name] = value
    if name == 'Source':
      self.load_source_components(self.config[name])
    self.savebutton.configure(state=tk.NORMAL)


  def generate_new_config(self):
    confutil.createConfig(self.confpath)
    confutil.updateConfig(self.confpath, 'FirstRun', False)
    self.mainframe.destroy()
    self.buttonframe.destroy()
    self.load_components()