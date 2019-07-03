import os, sys, json, platform
import tkinter as tk
from tkinter import ttk

import logging
from .. import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


class credentials_client:
  '''Instantiates a Tkinter frame that takes email settings and credentials to email new reports'''

  def __init__(self, parent, firstrun=False):
    self.parent = parent
    self.parent.configure(background='#ededed')
    self.firstrun = firstrun
    self.parent.resizable(width=False, height=False)
    self.parent.geometry('400x250')
    self.parent.title('CTQA Notification Credentials')
    try:
      img = tk.PhotoImage(file=resource_path('res/ctqa-icon.gif'))
      parent.tk.call('wm', 'iconphoto', parent._w, img)
    except tk.TclError:
      print("ERROR: Could not load ctqa-icon.gif from resources folder")

    # Setting up absolute locations
    self.location = os.path.abspath(os.path.dirname(sys.argv[0]))
    self.reportspath = os.path.join(self.location, 'reports')

    # Placing components
    self.load_components()

  
  def load_components(self):
    self.buttonframe = tk.Frame(self.parent, background='#ededed')
    self.savebutton = tk.Button(self.buttonframe, text='Save Credentials', width=20, command=self.save_creds, highlightbackground='#ededed')
    
    # Detecting if opened from client or first run
    if self.firstrun:
      self.closebutton = tk.Button(self.buttonframe, text='Next', width=10, command=self.exit_creds, highlightbackground='#ededed')
    else:
      self.closebutton = tk.Button(self.buttonframe, text='Close', width=10, command=self.exit_creds, highlightbackground='#ededed')
    self.savebutton.pack(side='left')
    self.closebutton.pack(side='right')
    self.buttonframe.pack(side='bottom', fill='x', padx=10, pady=(0,10))

    # Frame for config elements
    self.mainframe = tk.LabelFrame(self.parent, text='Credentials', background='#ededed')
    self.mainframe.pack(side='top', expand=True, fill='both', padx=10, pady=10)

    # Creating Protocol label and textbox
    self.protocollabel = tk.Label(self.mainframe, text='Protocol')
    self.protocolcombo = ttk.Combobox(self.mainframe, width=23, background='#ededed')
    self.protocolcombo['values'] = ['Exchange']
    self.protocolcombo.set('Exchange')
    self.protocolcombo['state'] = 'readonly'
    # Placing
    self.protocollabel.grid(column=0, row=0, sticky='w', padx=(10,0), pady=(10,10))
    self.protocolcombo.grid(column=1, row=0, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Email Address label and textbox
    self.addresslabel = tk.Label(self.mainframe, text='Email Address')
    self.addressentry = tk.Entry(self.mainframe, width=25, justify=tk.LEFT, highlightbackground='#ededed')
    self.addresslabel.grid(column=0, row=1, sticky='w', padx=(10,0), pady=(10,10))
    self.addressentry.grid(column=1, row=1, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Password label and textbox
    self.passwordlabel = tk.Label(self.mainframe, text='Password')
    self.passwordentry = tk.Entry(self.mainframe, width=25, show='*', justify=tk.LEFT, highlightbackground='#ededed')
    self.passwordlabel.grid(column=0, row=2, sticky='w', padx=(10,0), pady=(10,10))
    self.passwordentry.grid(column=1, row=2, sticky='e', padx=(0,10), pady=(10,10))

    # Creating Receiving email label and textbox
    self.recvlabel = tk.Label(self.mainframe, text='Receiver')
    self.recventry = tk.Entry(self.mainframe, width=25, justify=tk.LEFT, highlightbackground='#ededed')
    self.recvlabel.grid(column=0, row=3, sticky='w', padx=(10,0), pady=(10,10))
    self.recventry.grid(column=1, row=3, sticky='e', padx=(0,10), pady=(10,10))

    # Mainframe grid weight setup
    self.mainframe.grid_columnconfigure(0, weight=1)
    self.mainframe.grid_columnconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(0, weight=1)
    self.mainframe.grid_rowconfigure(1, weight=1)
    self.mainframe.grid_rowconfigure(2, weight=1)
    self.mainframe.grid_rowconfigure(3, weight=1)


  def save_creds(self):
    fkey = encryption.get_fernet_key()
    CREDS = {
      "Protocol": self.protocolcombo.get(),
      "EmailAddress": self.addressentry.get(),
      "Password": self.passwordentry.get(),
      "Receiver": self.recventry.get()
    }
    jsonstring = json.dumps(CREDS)
    token = fkey.encrypt(bytes(jsonstring, encoding='ascii'))
    
    # Saving token to file
    with open('data/enc', 'wb') as outfile:
      outfile.write(token)
      outfile.close()

  
  def exit_creds(self):
    self.parent.destroy()