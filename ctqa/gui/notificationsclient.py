import os, sys, json, platform
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .. import confutil
from .. import emailutil
from .. import encryption
import threading

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

    # Init test email variables
    self.test_email_resp = None
    self.test_email_message = None

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
    # Adding padding to left of save button to keep the window the same size when all is minimized
    self.savebutton.pack(side='left', padx=(0, 160))
    self.closebutton.pack(side='right')
    self.buttonframe.grid(column=0, row=6, sticky='we', padx=10, pady=10)

    # Creating email settings elements
    # Creating frame for expand panel for email settings
    self.button_email_settings = tk.LabelFrame(self.parent)
    self.button_email_settings.grid(column=0, row=0, sticky="we", padx=10, pady=(10,0))
    # Expand panel buttons
    self.email_settings_expand_label = tk.Label(self.button_email_settings, text='Email Sender Settings')
    self.email_settings_expand = tk.Button(self.button_email_settings, width=3, justify=tk.CENTER, text="+")
    self.email_settings_expand_label.grid(column=0, row=0, sticky='w', padx=(10,10), pady=5)
    self.email_settings_expand.grid(column=1, row=0, sticky='e', padx=(10,10), pady=5)
    self.button_email_settings.grid_columnconfigure(0, weight=1)
    self.button_email_settings.grid_columnconfigure(1, weight=0)
    # Email settings element creation
    self.create_email_settings()
    # Expand panel configure
    self.email_settings_expand.configure(command=lambda: self.toggle(self.emailframe))
    self.emailframe.grid_forget()

    # Creating frame for expand panel for email recipients
    self.button_email_recipients = tk.LabelFrame(self.parent)
    self.button_email_recipients.grid(column=0, row=2, sticky="we", padx=10, pady=(10,0))
    # Expand panel buttons
    self.email_recipients_expand_label = tk.Label(self.button_email_recipients, text='Email Recipients')
    self.email_recipients_expand = tk.Button(self.button_email_recipients, width=3, justify=tk.CENTER, text="+")
    self.email_recipients_expand_label.grid(column=0, row=0, sticky='w', padx=(10,10), pady=5)
    self.email_recipients_expand.grid(column=1, row=0, sticky='e', padx=(10,10), pady=5)
    self.button_email_recipients.grid_columnconfigure(0, weight=1)
    self.button_email_recipients.grid_columnconfigure(1, weight=0)
    # Creating email recipients elements
    self.create_email_recipients()
    # Expand panel configure
    self.email_recipients_expand.configure(command=lambda: self.toggle(self.recipframe))
    self.recipframe.grid_forget()

    # Creating frame for expand panel for hook settings
    self.button_hook_settings = tk.LabelFrame(self.parent)
    self.button_hook_settings.grid(column=0, row=4, sticky="we", padx=10, pady=(10,0))
    # Expand panel buttons
    self.hook_settings_expand_label = tk.Label(self.button_hook_settings, text='Hook Settings')
    self.hook_settings_expand = tk.Button(self.button_hook_settings, width=3, justify=tk.CENTER, text="+")
    self.hook_settings_expand_label.grid(column=0, row=0, sticky='w', padx=(10,10), pady=5)
    self.hook_settings_expand.grid(column=1, row=0, sticky='e', padx=(10,10), pady=5)
    self.button_hook_settings.grid_columnconfigure(0, weight=1)
    self.button_hook_settings.grid_columnconfigure(1, weight=0)
    # Creating hook settings elements
    self.create_hook_settings()
    # Expand panel configure
    self.hook_settings_expand.configure(command=lambda: self.toggle(self.mainframe))
    self.mainframe.grid_forget()


  def create_email_settings(self):
    # Frame for email elements
    self.emailframe = tk.LabelFrame(self.parent, background='#ededed')
    self.emailframe.grid(column=0, row=1, sticky='we', padx=10, pady=(0,5))
    self.emailframe.visible = False
    self.emailframe.row = 1

    # Creating email name label and textbox
    self.emaillabel = tk.Label(self.emailframe, text='Email')
    self.emailentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.emailentry.insert(0, self.config["Email"])
    self.emaillabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,5))
    self.emailentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,5))

    # Creating email password label and textbox
    self.passlabel = tk.Label(self.emailframe, text='Password')
    self.passentry = tk.Entry(self.emailframe, show="*", width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.passentry.insert(0, encryption.get_password())
    self.passlabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=5)
    self.passentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=5)

    # Creating email type dropdown
    self.servertypechoices = {"SMTP", "Exchange"}
    self.servertypevar = tk.StringVar(self.emailframe)
    if self.config["EmailServerType"] == "":
      self.servertypevar.set("SMTP")
    else:
      self.servertypevar.set(self.config["EmailServerType"])
    self.servertype = tk.OptionMenu(self.emailframe, self.servertypevar, *self.servertypechoices)
    self.servertypelabel = tk.Label(self.emailframe, text='Email Server Type')
    self.servertypelabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=0)
    self.servertype.grid(column=1, row=2, sticky='w', padx=(15,10), pady=0)

    # Creating email server label and textbox
    self.serverlabel = tk.Label(self.emailframe, text='Email Server')
    self.serverentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.serverlabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=5)
    self.serverentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=5)

    # Creating email server label and textbox
    self.portlabel = tk.Label(self.emailframe, text='Email Server Port')
    self.portentry = tk.Entry(self.emailframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.portlabel.grid(column=0, row=4, sticky='w', padx=(10,0), pady=5)
    self.portentry.grid(column=1, row=4, sticky='e', padx=(0,10), pady=5)

    self.checkemailbutton = tk.Button(self.emailframe, pady=5, padx=5, text="Test Connection to Email", command=self.test_email)
    self.checkemailbutton.grid(column=1, row=5, padx=10, pady=(0,10), sticky="e")

    # Emailframe grid weight setup
    self.emailframe.grid_columnconfigure(0, weight=1)
    self.emailframe.grid_columnconfigure(1, weight=1)
    self.emailframe.grid_rowconfigure(0, weight=1)
    self.emailframe.grid_rowconfigure(1, weight=1)
    self.emailframe.grid_rowconfigure(2, weight=1)
    self.emailframe.grid_rowconfigure(3, weight=1)
    self.emailframe.grid_rowconfigure(4, weight=1)
    self.emailframe.grid_rowconfigure(5, weight=1)


  def create_email_recipients(self):
    # Frame for email recipient elements
    self.recipframe = tk.LabelFrame(self.parent, background='#ededed')
    self.recipframe.grid(column=0, row=3, sticky='we', padx=10)
    self.recipframe.visible = False
    self.recipframe.row = 3

    # Creating daily recipients label and textbox
    self.dailyreciplabel = tk.Label(self.recipframe, text='Daily Reports')
    self.dailyrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.dailyrecipentry.insert(0, self.config["DailyRecipients"])
    self.dailyreciplabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,5))
    self.dailyrecipentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,5))

    # Creating weekly recipients label and textbox
    self.weeklyreciplabel = tk.Label(self.recipframe, text='Weekly Reports')
    self.weeklyrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.weeklyrecipentry.insert(0, self.config["WeeklyRecipients"])
    self.weeklyreciplabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=5)
    self.weeklyrecipentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=5)

    # Creating warning recipients label and textbox
    self.warningreciplabel = tk.Label(self.recipframe, text='Warnings')
    self.warningrecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.warningrecipentry.insert(0, self.config["WarningRecipients"])
    self.warningreciplabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=5)
    self.warningrecipentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=5)

    # Creating failure recipients label and textbox
    self.failurereciplabel = tk.Label(self.recipframe, text='Failures')
    self.failurerecipentry = tk.Entry(self.recipframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.failurerecipentry.insert(0, self.config["FailureRecipients"])
    self.failurereciplabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(5,10))
    self.failurerecipentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(5,10))

    # Recipframe grid weight setup
    self.recipframe.grid_columnconfigure(0, weight=1)
    self.recipframe.grid_columnconfigure(1, weight=1)
    self.recipframe.grid_rowconfigure(0, weight=1)
    self.recipframe.grid_rowconfigure(1, weight=1)
    self.recipframe.grid_rowconfigure(2, weight=1)
    self.recipframe.grid_rowconfigure(3, weight=1)


  def create_hook_settings(self):
    # Frame for config elements
    self.mainframe = tk.LabelFrame(self.parent, background='#ededed')
    self.mainframe.grid(column=0, row=5, sticky='we', padx=10)
    self.mainframe.visible = False
    self.mainframe.row = 5

    # Creating Failure hook label and textbox
    self.failurelabel = tk.Label(self.mainframe, text='Failure Hook')
    self.failureentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.failureentry.insert(0, self.config["FailureHook"])
    self.failurelabel.grid(column=0, row=0, sticky='w', padx=(10,10), pady=(10,5))
    self.failureentry.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,5))

    # Creating Warning hook label and textbox
    self.warninglabel = tk.Label(self.mainframe, text='Warning Hook')
    self.warningentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.warningentry.insert(0, self.config["WarningHook"])
    self.warninglabel.grid(column=0, row=1, sticky='w', padx=(10,10), pady=5)
    self.warningentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=5)

    # Creating Weekly Reports hook label and textbox
    self.weeklylabel = tk.Label(self.mainframe, text='Weekly Reports Hook')
    self.weeklyentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.weeklyentry.insert(0, self.config["WeeklyReportHook"])
    self.weeklylabel.grid(column=0, row=2, sticky='w', padx=(10,10), pady=5)
    self.weeklyentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=5)

    # Creating Daily reports hook label and textbox
    self.dailylabel = tk.Label(self.mainframe, text='Daily Reports Hook')
    self.dailyentry = tk.Entry(self.mainframe, width=35, justify=tk.LEFT, highlightbackground='#ededed')
    self.dailyentry.insert(0, self.config["DailyReportHook"])
    self.dailylabel.grid(column=0, row=3, sticky='w', padx=(10,10), pady=(5,10))
    self.dailyentry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(5,10))

    # Mainframe grid weight setup
    self.mainframe.grid_columnconfigure(0, weight=1)
    self.mainframe.grid_columnconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(0, weight=1)
    self.mainframe.grid_rowconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(2, weight=1)
    self.mainframe.grid_rowconfigure(3, weight=1)


  def toggle(self, frame):
    if frame.visible:
      frame.grid_forget()
      frame.visible = False
    else:
      frame.grid(column=0, row=frame.row, sticky='we', padx=10)
      frame.visible = True


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

    # Saving email values
    if not email == "":
      confutil.updateConfig(self.configpath, "Email", email)

    # Saving Email Settings
    confutil.updateConfig(self.configpath, "EmailServer", self.serverentry.get())
    confutil.updateConfig(self.configpath, "EmailServerType", self.servertypevar.get())
    confutil.updateConfig(self.configpath, "EmailServerPort", self.portentry.get())

    # Saving password
    encryption.save_password(self.passentry.get())

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


  def email_connect(self, address, password, servertype, serverhost, serverport, callback):
    resp, message = emailutil.test_connect(address, password, servertype, serverhost, serverport)
    self.test_email_resp = resp
    self.test_email_message = message
    callback()


  def test_email_notify(self):
    # re-enabling check button
    self.checkemailbutton.configure(state=tk.NORMAL, text="Test Connection to Email")
    if self.test_email_resp:
      messagebox.showinfo(parent=self.parent, title="Connection Success", message="Connection to email successful")
    else:
      messagebox.showerror(parent=self.parent, title="Connection Failure", message=self.test_email_message)

  
  def test_email(self):
    address = self.emailentry.get()
    password = self.passentry.get()
    servertype = self.servertypevar.get()
    serverhost = self.serverentry.get()
    serverport = None

    # If we're checking an SMTP connection, we need the port
    if servertype == "SMTP":
      try:
        serverport = int(self.portentry.get())
      except ValueError:
        messagebox.showerror(parent=self.parent, title="Invalid Port", message="Please enter a valid port number")
        return

    # Disabling check button
    self.checkemailbutton.configure(state=tk.DISABLED, text="Testing...")

    # Running the email connection test asynchronously
    thread = threading.Thread(target=self.email_connect, args=(address, password, servertype, serverhost, serverport, self.test_email_notify))
    thread.start()


  def exit_creds(self):
    self.parent.destroy()