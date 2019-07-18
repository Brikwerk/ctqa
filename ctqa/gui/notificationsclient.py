import os, sys, json, platform
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yagmail
from .. import confutil

import logging
from .. import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


class notifications_client:
  '''Instantiates a Tkinter frame that sets up email and hooks for CTQA events'''

  def __init__(self, parent, firstrun=False):
    self.parent = parent
    self.parent.configure(background='#ededed')
    self.firstrun = firstrun
    self.parent.resizable(width=False, height=False)
    self.parent.geometry('400x700')
    self.parent.title('CTQA Notification Settings')
    try:
      img = tk.PhotoImage(file=resource_path('res/ctqa-icon.gif'))
      parent.tk.call('wm', 'iconphoto', parent._w, img)
    except tk.TclError:
      print("ERROR: Could not load ctqa-icon.gif from resources folder")

    # Setting up absolute locations
    self.location = os.path.abspath(os.path.dirname(sys.argv[0]))
    self.reportspath = os.path.join(self.location, 'reports')
    self.configpath = os.path.join(self.location, confutil.DEFAULT_CONFIG_LOCATION)
    self.config = confutil.loadConfig(self.configpath)

    # Placing components
    self.load_components()

  
  def load_components(self):
    self.buttonframe = tk.Frame(self.parent, background='#ededed')
    self.savebutton = tk.Button(self.buttonframe, text='Save Settings', width=20, command=self.save_hooks, highlightbackground='#ededed')
    
    # Detecting if opened from client or first run
    if self.firstrun:
      self.closebutton = tk.Button(self.buttonframe, text='Next', width=10, command=self.exit_creds, highlightbackground='#ededed')
    else:
      self.closebutton = tk.Button(self.buttonframe, text='Close', width=10, command=self.exit_creds, highlightbackground='#ededed')
    self.savebutton.pack(side='left')
    self.closebutton.pack(side='right')
    self.buttonframe.pack(side='bottom', fill='x', padx=10, pady=(0,10))

    # Frame for email elements
    self.emailframe = tk.LabelFrame(self.parent, text='Email Sender Settings', background='#ededed')
    self.emailframe.pack(side='top', expand=True, fill='both', padx=10, pady=10)

    # Creating email name label and textbox
    self.emaillabel = tk.Label(self.emailframe, text='Email')
    self.emailentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.emailentry.insert(0, self.config["Email"])
    self.emaillabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,10))
    self.emailentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,10))

    # Creating email password label and textbox
    self.passlabel = tk.Label(self.emailframe, text='Password')
    self.passentry = tk.Entry(self.emailframe, show="*", width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.passlabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(10,10))
    self.passentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(10,10))

    # Creating email type dropdown
    self.servertypechoices = {"SMTP", "IMAP", "POP3", "Exchange"}
    self.servertypevar = tk.StringVar(self.emailframe)
    if self.config["EmailServerType"] == "":
      self.servertypevar.set("SMTP")
    else:
      self.servertypevar.set(self.config["EmailServerType"])
    self.servertype = tk.OptionMenu(self.emailframe, self.servertypevar, *self.servertypechoices)
    self.servertypelabel = tk.Label(self.emailframe, text='Email Server Type')
    self.servertypelabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=(10,10))
    self.servertype.grid(column=1, row=2, sticky='w', padx=(20,10), pady=(10,10))

    # Creating email server label and textbox
    self.serverlabel = tk.Label(self.emailframe, text='Email Server')
    self.serverentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.serverlabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(10,10))
    self.serverentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(10,10))

    # Creating email server label and textbox
    self.portlabel = tk.Label(self.emailframe, text='Email Server Port')
    self.portentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.portlabel.grid(column=0, row=4, sticky='w', padx=(10,0), pady=(10,10))
    self.portentry.grid(column=1, row=4, sticky='e', padx=(0,10), pady=(10,10))

    # Emailframe grid weight setup
    self.emailframe.grid_columnconfigure(0, weight=1)
    self.emailframe.grid_columnconfigure(1, weight=1)
    self.emailframe.grid_rowconfigure(0, weight=1)
    self.emailframe.grid_rowconfigure(1, weight=1)
    self.emailframe.grid_rowconfigure(2, weight=1)
    self.emailframe.grid_rowconfigure(3, weight=1)
    self.emailframe.grid_rowconfigure(4, weight=1)

    # Frame for email recipient elements
    self.recipframe = tk.LabelFrame(self.parent, text='Email Recipients', background='#ededed')
    self.recipframe.pack(side='top', expand=True, fill='both', padx=10, pady=10)

    # Creating daily recipients label and textbox
    self.dailyreciplabel = tk.Label(self.recipframe, text='Daily Reports')
    self.dailyrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.dailyrecipentry.insert(0, self.config["DailyRecipients"])
    self.dailyreciplabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,10))
    self.dailyrecipentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,10))

    # Creating weekly recipients label and textbox
    self.weeklyreciplabel = tk.Label(self.recipframe, text='Weekly Reports')
    self.weeklyrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.weeklyrecipentry.insert(0, self.config["WeeklyRecipients"])
    self.weeklyreciplabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(10,10))
    self.weeklyrecipentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(10,10))

    # Creating warning recipients label and textbox
    self.warningreciplabel = tk.Label(self.recipframe, text='Warnings')
    self.warningrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.warningrecipentry.insert(0, self.config["WarningRecipients"])
    self.warningreciplabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=(10,10))
    self.warningrecipentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=(10,10))

    # Creating failure recipients label and textbox
    self.failurereciplabel = tk.Label(self.recipframe, text='Failures')
    self.failurerecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.failurerecipentry.insert(0, self.config["FailureRecipients"])
    self.failurereciplabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(10,10))
    self.failurerecipentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(10,10))

    # Recipframe grid weight setup
    self.recipframe.grid_columnconfigure(0, weight=1)
    self.recipframe.grid_columnconfigure(1, weight=1)
    self.recipframe.grid_rowconfigure(0, weight=1)
    self.recipframe.grid_rowconfigure(1, weight=1)
    self.recipframe.grid_rowconfigure(2, weight=1)
    self.recipframe.grid_rowconfigure(3, weight=1)

    # Frame for config elements
    self.mainframe = tk.LabelFrame(self.parent, text='Hooks', background='#ededed')
    self.mainframe.pack(side='top', expand=True, fill='both', padx=10, pady=10)

    # Creating Failure hook label and textbox
    self.failurelabel = tk.Label(self.mainframe, text='Failure Hook')
    self.failureentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.failureentry.insert(0, self.config["FailureHook"])
    self.failurelabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,10))
    self.failureentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Warning hook label and textbox
    self.warninglabel = tk.Label(self.mainframe, text='Warning Hook')
    self.warningentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.warningentry.insert(0, self.config["WarningHook"])
    self.warninglabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(10,10))
    self.warningentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Weekly Reports hook label and textbox
    self.weeklylabel = tk.Label(self.mainframe, text='Weekly Reports Hook')
    self.weeklyentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.weeklyentry.insert(0, self.config["WeeklyReportHook"])
    self.weeklylabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=(10,10))
    self.weeklyentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Daily reports hook label and textbox
    self.dailylabel = tk.Label(self.mainframe, text='Daily Reports Hook')
    self.dailyentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.dailyentry.insert(0, self.config["DailyReportHook"])
    self.dailylabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(10,10))
    self.dailyentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(10,10))

    # Mainframe grid weight setup
    self.mainframe.grid_columnconfigure(0, weight=1)
    self.mainframe.grid_columnconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(0, weight=1)
    self.mainframe.grid_rowconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(2, weight=1)
    self.mainframe.grid_rowconfigure(3, weight=1)


  def save_hooks(self):
    """Validates and saves all paths entered into the notification entry components"""
    hookpaths = [self.failureentry.get(), self.warningentry.get(), self.weeklyentry.get(), self.dailyentry.get()]
    configkeys = ["FailureHook", "WarningHook", "WeeklyReportHook", "DailyReportHook"]

    for i in range(0, len(hookpaths)):
      paths = hookpaths[i]
      key = configkeys[i]
      validationresult = self.validate_hook(paths)
      if validationresult:
        confutil.updateConfig(self.configpath, key, paths)
      else:
        messagebox.showerror("Hook Path Error", str(key) + " does not contain a valid path.\n Please enter a valid path separated by semicolons.", parent=self.parent)
    
    # Getting user entered email values
    email = self.emailentry.get()
    password = self.passentry.get()

    # Saving email values
    if not email == "":
      yagmail.register(email, password)
      confutil.updateConfig(self.configpath, "Email", email)

    # Saving recipients
    confutil.updateConfig(self.configpath, "DailyRecipients", self.dailyrecipentry.get())
    confutil.updateConfig(self.configpath, "WeeklyRecipients", self.weeklyrecipentry.get())
    confutil.updateConfig(self.configpath, "WarningRecipients", self.warningrecipentry.get())
    confutil.updateConfig(self.configpath, "FailureRecipients", self.failurerecipentry.get())


  def validate_hook(self, paths):
    paths = paths.split(";")
    result = True

    try:
      for path in paths:
        abspath = os.path.abspath(path)
        if os.path.isfile(abspath) or os.path.isdir(abspath):
          continue
        else:
          result = False
      return result
    except Exception:
      return False

  
  def exit_creds(self):
    self.parent.destroy()