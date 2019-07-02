'''
CTQA Client Module

Contains logic for implementing the CTQA Client with the ctqa_client class.
'''

import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
from tkinter import messagebox
from PIL import Image, ImageTk
from collections import deque
from .. import servicemanager
from .. import reportutil
from . import profileclient
from . import configclient
from . import credclient
from . import logwatcher
from .. import confutil
import win32com.client
import subprocess
import threading
import datetime
import platform
import time
import glob
import sys
import os

import logging
from .. import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


class ctqa_client:
  '''CTQA client class. Contains logic to instantiate inside a passed Tkinter parent element.'''

  def __init__(self, parent):
    self.parent = parent
    self.parent.minsize(600,400)
    self.parent.geometry('750x500')
    self.parent.title('CTQA Client')
    try:
      img = tk.PhotoImage(file=resource_path('res/ctqa-icon.gif'))
      parent.tk.call('wm', 'iconphoto', parent._w, img)
    except tk.TclError:
      logger.error("ERROR: Could not load ctqa-icon.gif from resources folder")

    self.location = os.path.abspath(os.path.dirname(sys.argv[0]))
    self.logpath = self.location + '/ctqa.log'
    self.confpath = self.location + '/config.json'
    self.reportspath = self.location + '/reports'
    self.config = confutil.loadConfig(self.confpath)

    self.mainfrm_style = ttk.Style()
    self.mainfrm_style.configure('Main.TFrame')
    self.mainfrm = ttk.Frame(self.parent, style='Main.TFrame', padding=(10, 5, 10, 5))
    self.mainfrm.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    # Menubar
    self.createMenubar()

    # Report section
    self.createReportList()
    self.createReportElements()
    self.createLogElements()

    #Service section
    self.createServiceDisplay()

    # Weighting elements for resizing
    # Col/Rows of Root
    self.parent.columnconfigure(0, weight=1)
    self.parent.rowconfigure(0, weight=1)
    # Cols of Main Frame
    self.mainfrm.columnconfigure(0, weight=0)
    self.mainfrm.columnconfigure(1, weight=1)
    self.mainfrm.columnconfigure(2, weight=1)
    self.mainfrm.columnconfigure(3, weight=2)
    self.mainfrm.columnconfigure(4, weight=2)
    # Rows of Main Frame
    self.mainfrm.rowconfigure(1, weight=1)
    self.mainfrm.rowconfigure(2, weight=7)

    self.parent.attributes("-topmost", True)
    self.parent.attributes('-topmost', 0)

  
  def createMenubar(self):
    menubar = tk.Menu(self.parent)

    # Create CTQA pulldown menu
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=self.parent.quit)
    menubar.add_cascade(label="CTQA", menu=filemenu)

    # Create Reports pulldown menu
    # Daily report regen
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Regenerate Daily Reports", command=lambda: reportutil.regenerateReports(
      os.path.join(self.location, "data"),
      self.config
    ))
    # Weekly report regen
    menubar.add_cascade(label="Reports", menu=editmenu)
    editmenu.add_command(label="Regenerate Weekly Reports", command=lambda: reportutil.regenerateReports(
      os.path.join(self.location, "data"),
      self.config,
      report_type="weekly"
    ))
    menubar.add_cascade(label="Reports", menu=editmenu)

    # Display menu
    self.parent.config(menu=menubar)


  def createReportList(self):
    self.repframe = tk.Frame(self.mainfrm)
    self.repframe.grid(column=0, row=1, columnspan=3, rowspan=2)
    
    self.replist = ttk.Treeview(self.repframe, selectmode='browse')
    self.replist.pack(side='left', fill='both', expand=True)
    
    self.repscroll = ttk.Scrollbar(self.repframe, orient='vertical', command=self.replist.yview)
    self.repscroll.pack(side='right', fill='y')
    
    self.replist.configure(yscrollcommand=self.repscroll.set)
    
    self.replist['columns'] = ('1', '2')
    self.replist['show'] = 'headings'
    
    self.replist.column('1', width=100, anchor='w')
    self.replist.column('2', width=30, anchor='c')

    #Header names with sort code
    self.replist.heading('1',
      text='Report Name',
      command=lambda: self.treeview_sort_column(self.replist, '1', False)
    )
    self.replist.heading('2',
      text='Last Updated',
      command=lambda: self.treeview_sort_column(self.replist, '2', False)
    )

    self.populate_report_list()
    self.watch_reports_folder()
    self.replist.bind('<Double-Button-1>', self.open_report)


  def createReportElements(self):
    self.rlblframe = tk.Frame(self.mainfrm, background='#2f3f54')
    self.rlbl = tk.Label(self.rlblframe,
      text='Reports',
      foreground='#e3e9f0',
      background='#2f3f54',
      font=(12)
    )
    self.rlbl.pack(side='left', padx=5)

    self.rOpen = tk.Button(self.mainfrm, text='Open Reports Folder', highlightbackground='#e6e6e6', command=self.open_reports_folder)
    self.rView = tk.Button(self.mainfrm, text='View Report', highlightbackground='#e6e6e6', command=self.open_report)
    #Adding to grid
    self.repframe.grid(column=0, row=1, columnspan=3, rowspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
    self.rlblframe.grid(column=0, row=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W))
    self.rOpen.grid(column=0, row=3, sticky=(tk.N, tk.W), pady=5)
    self.rView.grid(column=2, row=3, sticky=(tk.N, tk.E), pady=5)


  def createServiceDisplay(self):
    # Creating settings title bar
    self.sFrame = tk.Frame(self.mainfrm, background='#2f3f54')
    self.slbl = tk.Label(self.sFrame,
      text='CTQA Audit',
      foreground='#e3e9f0',
      background='#2f3f54',
      font=(12)
    )
    self.slbl.pack(side='left', padx=5)
    self.sFrame.grid(column=3, row=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(10,0))

    #Creating the frame for all ctqa-service settings/config controls
    self.settingsFrame = tk.Frame(self.mainfrm, height=150, background='#ddd', relief=tk.SUNKEN, borderwidth=1)
    self.settingsFrame.grid(
      column=3, 
      row=1, 
      columnspan=3, 
      sticky=(tk.N, tk.S, tk.E, tk.W),
      padx=(10, 0),
      pady=(0, 10)
    )

    # Creating CTQA Service status
    self.statusFrame = tk.LabelFrame(self.settingsFrame, height=150, width=130, text='Status', borderwidth=1, relief=tk.SUNKEN, background='#ccc')
    self.statusFrame.pack_propagate(0)
    self.statusFrame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    try:
      self.statImg = Image.open(resource_path('res/service-unreg.gif'))
      self.statImgTk = ImageTk.PhotoImage(self.statImg)
    except FileNotFoundError:
      logger.error("ERROR: Could not load service-unreg.gif from resources folder")

    #Fetching Source status
    if isinstance(self.config, int):
      srcres = None
    else:
      srcres = self.config.get('Source')

    # Source status
    self.sourcestatus = tk.Label(self.statusFrame, anchor=tk.CENTER, text="Source: " + str(srcres), bg='#ccc')
    self.sourcestatus.pack(expand=True, side='top', fill='x')

    # Creating CTQA config buttons frame
    self.configFrame = tk.Frame(self.settingsFrame, height=300, width=100, background='#ddd')
    self.configFrame.pack(side='right', expand=True, fill='x', padx=(0,10))

    # Creating CTQA config buttons
    # Start service
    self.configServiceControl = tk.Button(self.configFrame, text="Notifications", highlightbackground='#ddd', command=self.open_credentials_client)
    self.configServiceControl.pack(expand=True, fill='x', pady=(0,2))
    # Service (un)install
    if not self.config.get("ServicesInstalled"):
      self.configServiceInst = tk.Button(self.configFrame, text="Install Service", highlightbackground='#ddd', command=self.service_install)
      self.configServiceInst.pack(expand=True, fill='x', pady=(0,10))
    else:
      self.configServiceInst = tk.Button(self.configFrame, text="Uninstall Service", highlightbackground='#ddd', command=self.service_uninstall)
      self.configServiceInst.pack(expand=True, fill='x', pady=(0,10))
    # Manual Run
    self.configServiceRun = tk.Button(self.configFrame, text="Manual Audit", highlightbackground='#ddd', command=self.manual_audit)
    self.configServiceRun.pack(expand=True, fill='x', pady=(0,2))
    # Edit Config
    self.configServiceConfig = tk.Button(self.configFrame, text="Edit Config", highlightbackground='#ddd', command=self.open_config_client)
    self.configServiceConfig.pack(expand=True, fill='x', pady=(0,2))
    # Manage QA Profiles
    self.configServiceProfiles = tk.Button(self.configFrame, text="Manage QA Profiles", highlightbackground='#ddd', command=self.open_profile_client)
    self.configServiceProfiles.pack(expand=True, fill='x')


  def createLogElements(self):
    # Creating log frame
    self.lFrame = tk.Frame(self.mainfrm, background='#ddd', borderwidth=1, relief=tk.SUNKEN)
    self.lFrame.grid(
      column=3, 
      row=2, 
      columnspan=2, 
      rowspan=2, 
      sticky=(tk.N, tk.S, tk.E, tk.W),
      padx=(10,0)
    )

    # Creating log title bar
    self.llblFrame = tk.Frame(self.lFrame, background='#2f3f54', height=20)
    self.llblFrame.pack(side='top', fill='x')
    self.llbl = tk.Label(self.llblFrame,
      text='Logs',
      foreground='#e3e9f0',
      background='#2f3f54',
      font=(12)
    )
    self.llbl.pack(side='left', padx=5)

    # Log Button frame
    self.logButtonFrame = tk.Frame(self.lFrame, background='#ddd')
    self.logButtonFrame.pack(side='bottom', fill='x')
    self.openLogButton = tk.Button(self.logButtonFrame, text='Open Log', highlightbackground='#ddd', command=self.open_log)
    self.openLogFolderButton = tk.Button(self.logButtonFrame, text='Open Log Folder', highlightbackground='#ddd', command=self.open_log_folder)
    self.openLogFolderButton.pack(side='right', padx=(5,10), pady=5)
    self.openLogButton.pack(side='right', padx=(5,0))

    # Textbox + scrollbar in logTextFrame
    self.logTextFrame = tk.Frame(self.lFrame, background='#ffffff')
    self.logTextFrame.pack(side='top', expand=True, fill='both')

    self.logTextScrollY = ttk.Scrollbar(self.logTextFrame, orient='vertical')
    self.logTextScrollY.pack(side='right', fill='y')

    self.logTextScrollX = ttk.Scrollbar(self.logTextFrame, orient='horizontal')
    self.logTextScrollX.pack(side='bottom', fill='x')

    self.logText = tk.Text(self.logTextFrame, width=40, border=0, wrap=tk.NONE,
      xscrollcommand=self.logTextScrollX.set,
      yscrollcommand=self.logTextScrollY.set
    )
    self.logText.pack(side='bottom', expand=True, fill='both')
    
    self.logTextScrollX.config(command=self.logText.xview)
    self.logTextScrollY.config(command=self.logText.yview)

    # Adding log watcher, whether or not log exists
    self.start_log_watcher()
    
    # Adding log contents if log exists
    if os.path.isfile(self.logpath):
      self.load_log_contents()
      self.logText.see(tk.END) # Scrolling to bottom of textbox
    else:
      self.logText.insert('end', 'Log either does not exist yet or could not be found.')

  def treeview_sort_column(self, tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
               self.treeview_sort_column(tv, col, not reverse))

  
  def checkForFolder(self, path, name):
    folderExists = os.path.isdir(path)

    if folderExists:
      return path
    else:
      messagebox.showerror(name + " Error", name + " folder does not exist at location:\n" + path, parent=self.parent)
      return False


  def populate_report_list(self):
    reportsFolder = os.path.isdir(self.reportspath)

    if reportsFolder:
      pngs = []
      for file in glob.glob(self.reportspath + '/*.png'):
        fileName = os.path.basename(os.path.splitext(file)[0])
        mTime = os.path.getmtime(file)
        pngs.append([fileName, mTime])
      
      if len(pngs) == 0:
        self.replist.insert('', 'end', text='Audit Report', values=('Reports folder is empty',''))
      else:
        #Iterates over name/unix timestamp from iterated pngs and inserts into replist
        for png in pngs:
          mTime = datetime.datetime.fromtimestamp(png[1]).strftime('%Y-%m-%d %H:%M:%S')
          self.replist.insert('', 'end', text='Audit Report', values=(png[0],mTime))
    else:
      self.replist.insert('', 'end', text='Audit Report', values=('Could not open reports folder',''))


  def refresh_report(self):
    self.replist.delete(*self.replist.get_children())
    self.populate_report_list()

  # Watches for name/time changes and updates folder
  def watch_reports_folder(self):
    def watchReports():
      print('Started watching reports folder')
      oldReports = []
      while True:
        repFolderExists = os.path.isdir(self.reportspath)
        if repFolderExists:
          reports = glob.glob(self.reportspath + '/*.png')
          newReports = []
          for report in reports: # Detecting time created change
            try:
              newReports.append(report) 
              newReports.append(os.path.getmtime(report))
            except FileNotFoundError: # In case the user saves over the old report
              oldReports = []
          changes = set(newReports).symmetric_difference(set(oldReports))
          if changes != set():  #If there's new changes in the folder
            print("Report folder change detected")
            self.refresh_report()
            oldReports = newReports
          time.sleep(1)
        else:
          oldReports = []
          self.refresh_report()
          time.sleep(1)
    thread = threading.Thread(target=watchReports)
    thread.daemon = True
    thread.start()


  def open_reports_folder(self):
    reportsLocation = self.checkForFolder(self.reportspath, 'Report')

    if reportsLocation:
      if platform.system() == "Windows":
          os.startfile(reportsLocation)
      elif platform.system() == "Darwin":
          subprocess.Popen(["open", reportsLocation])
      else:
          subprocess.Popen(["xdg-open", reportsLocation])

  
  def open_report(self, event=None):
    rlist = self.replist
    report = rlist.item(rlist.focus())
    if report['text'] == '':
      return
    else:
      reportsLocation = self.checkForFolder(self.reportspath, 'Report')
      if reportsLocation:
        reportPath = reportsLocation + '/' + report['values'][0] + '.png'
        if os.path.isfile(reportPath):
          if platform.system() == "Windows":
              os.startfile(reportPath)
          elif platform.system() == "Darwin":
              subprocess.Popen(["open", reportPath])
          else:
              subprocess.Popen(["xdg-open", reportPath])
        else:
          messagebox.showerror("Report Error", "Report does not exist at:\n" + reportPath)


  def load_log_contents(self):
    d = None
    with open(self.logpath) as f:
      d=deque(f, maxlen=250)
    
    while True:
      try:
        self.logText.insert('end', d.popleft())
      except IndexError:
        break

    self.logText.configure(state='disabled')


  def refresh_log(self):
    self.logText.configure(state='normal')
    self.logText.delete('1.0', tk.END)
    self.load_log_contents()
    self.logText.see(tk.END)


  def start_log_watcher(self):
    def watchLog(callback):
      lw = logwatcher.LogWatcher(self.location, callback)
      lw.loop()
    thread = threading.Thread(target=watchLog, args=(self.log_watcher_callback,))
    thread.daemon = True
    thread.start()

    return thread

  def log_watcher_callback(self, file, lines):
    self.logText.configure(state='normal')
    for line in lines:
      self.logText.insert('end', line)
      self.logText.see(tk.END)
    self.logText.configure(state='disabled')


  def open_log(self):
    logExists = os.path.isfile(self.logpath)
    if logExists:
      if platform.system() == "Windows":
          os.startfile(self.logpath)
      elif platform.system() == "Darwin":
          subprocess.Popen(["open", self.logpath])
      else:
          subprocess.Popen(["xdg-open", self.logpath])


  def open_log_folder(self):
    logLocation = self.checkForFolder(self.location, 'Log')
    if logLocation:
      if platform.system() == "Windows":
          os.startfile(logLocation)
      elif platform.system() == "Darwin":
          subprocess.Popen(["open", logLocation])
      else:
          subprocess.Popen(["xdg-open", logLocation])


  def manual_audit(self):
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
      command = sys.argv[0] + ' --audit --debug'
    else:
      command = 'python ' + sys.argv[0] + ' --audit --debug'
    self.popenAndCall(self.resetButton, command)


  def resetButton(self):
    self.configServiceRun.configure(state='normal')
    self.configServiceRun.configure(text='Manual Audit')
  

  def popenAndCall(self, onExit, command):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that 
    would give to subprocess.Popen.
    """
    def runInThread(onExit, command):
      self.configServiceRun.configure(text='Running...')
      self.configServiceRun.configure(state='disabled')
      proc = subprocess.Popen(command.split())
      proc.wait()
      onExit()
      return
    thread = threading.Thread(target=runInThread, args=(onExit, command))
    thread.start()
    # returns immediately after the thread starts
    return thread


  def open_config_client(self):
    top = Toplevel()
    configclient.config_client(top)


  def open_profile_client(self):
    top = Toplevel()
    profileclient.profile_client(top)


  def open_credentials_client(self):
    top = Toplevel()
    credclient.credentials_client(top)


  def service_install(self):
    # Attempt a service manager install
    servicemanager.install()
    self.configServiceInst.configure(text='Uninstall Service')
    self.configServiceInst.configure(command=self.service_uninstall)


  def service_uninstall(self):
    # Attempt to uninstall service
    servicemanager.uninstall()
    self.configServiceInst.configure(text='Install Service')
    self.configServiceInst.configure(command=self.service_install)
