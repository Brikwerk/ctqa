'''
First Run Module

Contains logic for aiding in a user's first run of the CTQA application.
'''


import os, sys
import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
from tkinter import messagebox
from ctqa.gui import profileclient
from ctqa.gui import configclient
from ctqa.gui import client
from . import confutil

#Contants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))
confPath = LOCATION + "/" + confutil.DEFAULT_CONFIG_LOCATION


def run():
  '''
  The function run on the CTQA applications first run.

  The user is asked if they want to run through a guided setup. If they agree,
  they are taken through filling out the configuration and profile values. At
  the end, the regular CTQA application GUI is started and shown.
  '''

  # Creating initial root tkinter application
  root = tk.Tk()
  root.withdraw()

  msg = 'This appears to be the first run of the application. Would you like to perform a first time setup?'
  root.update()
  resp = messagebox.askyesno('CTQA Initial Run', msg) # Asking if user wants to setup
  if resp == False: # If not, we update the config and start the regular client
    confutil.updateConfig(confPath, "FirstRun", False)
    client.ctqa_client(root)
    root.deiconify()
    root.mainloop()
  else: # If they do, we start the setup
    root.update() # Must update before displaying a messagebox
    messagebox.showinfo('Config Setup', 'Please select the appropriate configuration values.')

    setup = Toplevel() # Setting up the config client on a top level
    configclient.config_client(setup, firstrun=True)
    while True: # Update config client until the user either saves (which closes) or closes
      root.update()
      if not setup.winfo_exists(): # When the setup toplevel is destroyed, break
        break

    # Telling user about profile configuration
    messagebox.showinfo('Audit Profile Setup', 'Please configure the audit profiles to your liking.')
    
    # Profile client is hosted on the root
    profileclient.profile_client(root, firstrun=True)
    root.deiconify()
    root.attributes('-topmost', 1)
    root.attributes('-topmost', 0)
    root.mainloop() # Profile client's mainloop quits on exit
    root.destroy()
    
    #Writing to config that we finished the first run setup
    confutil.updateConfig(confPath, "FirstRun", False)

    # After the user finishes their setup, we start the regular client
    root = tk.Tk()
    client.ctqa_client(root)
    root.mainloop()