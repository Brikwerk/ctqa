import os, sys, json, platform, copy
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
from tkinter import ttk
import threading

import logging
from .. import logutil
from .. import profileutil
from .. import autoprofiles
from .. import auditmethods
from . import selectlist
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


class profile_client:
  def __init__(self, parent, firstrun=False):
    self.parent = parent
    self.firstrun = firstrun
    self.parent.configure(background='#ededed')
    self.parent.resizable(width=False, height=False)
    if platform.system() == 'Darwin':
      self.parent.geometry('750x500')
    else:
      self.parent.geometry('650x500')
    self.parent.title('CTQA Audit Profiles')
    try:
      img = tk.PhotoImage(file=resource_path('res/ctqa-icon.gif'))
      parent.tk.call('wm', 'iconphoto', parent._w, img)
    except tk.TclError:
      print("ERROR: Could not load ctqa-icon.gif from resources folder")

    # Setting up absolute locations
    self.location = os.path.abspath(os.path.dirname(sys.argv[0]))
    self.logpath = self.location + '/ctqa.log'
    self.confpath = self.location + '/config.json'
    self.reportspath = self.location + '/reports'
    self.profilepath = self.location + '/profiles.json'

    #Setting up component count
    self.tempid = 0

    #Attempting to get profiles
    self.profiles = profileutil.openProfiles(self.profilepath)
    self.profilesToAdd = {}
    self.profilesChanged = False

    # Placing components
    self.load_components()

    # Binding keyboard shortcuts
    # Ctrl-Shift-S => Save and Quit
    self.parent.bind('<Control-Shift-Key-S>', lambda event: self.save_and_quit())
  

  def load_components(self):
    # Save and close buttons
    self.buttonframe = tk.Frame(self.parent, background='#ededed')
    self.savebutton = tk.Button(self.buttonframe, text='Save Profiles', width=20, state=tk.DISABLED, command=self.save_profiles, highlightbackground='#ededed')
    
    # Detecting if opened from client or first run
    if self.firstrun:
      self.closebutton = tk.Button(self.buttonframe, text='Next', width=10, command=self.exit_client, highlightbackground='#ededed')
    else:
      self.closebutton = tk.Button(self.buttonframe, text='Close', width=10, command=self.exit_client, highlightbackground='#ededed')
    self.closebutton.pack(side='right')
    self.savebutton.pack(side='right', padx=(0,15))
    self.buttonframe.pack(side='bottom', fill='x', padx=15, pady=15)

    # Frame for client elements
    self.mainframe = tk.Frame(self.parent, borderwidth=1, relief=tk.SUNKEN, background='#ededed')
    self.mainframe.pack(side='top', expand=True, fill='both', padx=15, pady=(15,0))

    # Creating profile display and profile settings display
    # If the profiles didn't load, offer to create profiles
    if not isinstance(self.profiles, dict):
      self.mainframe.configure(background='#ddd')
      self.errMsg = tk.Label(self.mainframe, background='#ddd', text='Error: Could not load profiles.\n\n Would you like to:')
      self.genProfs = tk.Button(self.mainframe, highlightbackground='#ddd', text="Auto Find Profiles", width=23, command=self.auto_profiles)
      self.manProfs = tk.Button(self.mainframe, highlightbackground='#ddd', text="Enter Profiles Manually", width=23, command=self.manual_profiles)
      self.errMsg.grid(row=1, column=1, columnspan=2, sticky='s')
      self.genProfs.grid(row=2, column=1, sticky='ne', pady=(10,0), padx=(0,5))
      self.manProfs.grid(row=2, column=2, sticky='nw', pady=(10,0), padx=(5,0))

      self.mainframe.grid_rowconfigure(1, weight=1)
      self.mainframe.grid_rowconfigure(2, weight=1)
      self.mainframe.grid_columnconfigure(1, weight=1)
      self.mainframe.grid_columnconfigure(2, weight=1)
    else:
      #Reconfiguring old elements and adding auto profile
      self.mainframe.configure(borderwidth=0)
      self.genProfs = tk.Button(self.buttonframe, highlightbackground='#ededed', text="Auto Find Profiles", width=23, command=self.auto_profiles)
      self.genProfs.pack(side='left')

      # Profile selection frame
      self.profsel = tk.Frame(self.mainframe, bg='#fff', highlightbackground="#999", highlightcolor="#999", highlightthickness=1, borderwidth=0)
      
      # Profile information frame
      self.profinfo = tk.Frame(self.mainframe, bg='#ddd', borderwidth=1, relief=tk.SUNKEN)
      # Adding container for info in profinfo
      self.profinfocont = tk.Frame(self.profinfo)
      self.profinfocont.pack(side='top', expand=True, fill='both')

      # Setting up profile selection
      self.profsel.grid(column=0, row=0, sticky='nsew', padx=(0,10))
      self.profinfo.grid(column=1, row=0, sticky='nsew')

      self.mainframe.grid_rowconfigure(0, weight=1)
      self.mainframe.grid_columnconfigure(0, weight=2)
      self.mainframe.grid_columnconfigure(1, weight=1)

      # Adding buttons to profile selection
      self.profselbuttons = tk.Frame(self.profsel)
      # Button styling for mac
      if platform.system() == 'Darwin':
        self.profselbuttons.configure(background='#ddd')

      # Add button
      self.profadd = tk.Button(self.profselbuttons, text='', height=24, width=29, highlightbackground='#ededed',borderwidth=0)
      # Add button styling on mac
      if platform.system() == 'Darwin':
        self.profadd.configure(highlightbackground='#ddd')
      try:
        self.profaddimage = tk.PhotoImage(file=resource_path('res/add.gif'))
        self.profadd.config(image=self.profaddimage)
        self.profadd.image = self.profaddimage
      except tk.TclError:
        self.profadd.config(text='+')
        logger.error("Unable to load add profiles button image")
        pass

      #Del button
      self.profdel = tk.Button(self.profselbuttons, text='', height=24, width=29, highlightbackground='#ededed', borderwidth=0)
      # Del button styling on mac
      if platform.system() == 'Darwin':
        self.profdel.configure(highlightbackground='#ddd')
      try:
        self.profdelimage = tk.PhotoImage(file=resource_path('res/del.gif'))
        self.profdel.config(image=self.profdelimage)
        self.profdel.image = self.profaddimage
      except tk.TclError:
        self.profdel.config(text='-')
        logger.error("Unable to load delete profiles button image")
        pass
      
      self.profselbuttons.pack(side='bottom', fill='both')
      self.profadd.pack(side='left', anchor='center', pady=(3,0))
      self.profdel.pack(side='left', anchor='center', pady=(3,0))
      self.profadd.configure(command=self.add_profile)
      self.profdel.configure(command=self.remove_profile)

      # Creating list
      self.proflist = selectlist.select_list(self.profsel, background='#fff')
      self.proflist.pack(side='top', anchor='center', expand=True, fill='both')

      for profile in self.profiles.keys():
        self.proflist.add(
          self.profiles[profile]['StationName'],
          self.profiles[profile]['Manufacturer'],
          profile
        )

      # Binding display_info to select event for proflist
      self.proflist.bind_select_callback(self.display_info)
      # Attempting to display info from selected profile
      if self.proflist.selected != None:
        self.display_info(self.proflist.selected)


  def display_info(self, id):
    if self.profinfocont.winfo_exists():
      self.profinfocont.destroy()

    # Recreating container for info in profinfo
    self.profinfocont = tk.Frame(self.profinfo, bg='#ddd')
    self.profinfocont.pack(side='top', expand=True, fill='both', pady=(0,10))

    # Getting profile settings from profilesToAdd or profiles
    if self.profiles.get(id):
      profile = self.profiles[id]
    elif self.profilesToAdd.get(id):
      profile = self.profilesToAdd[id]
    else:
      print('Profile with id: %s could not be found' % id)
      return -1

    # Labels
    self.profinfoname = tk.Label(self.profinfocont, text='Station Name:', highlightbackground='#ddd', bg='#ddd')
    self.profinfomanf = tk.Label(self.profinfocont, text='Manufacturer:', highlightbackground='#ddd', bg='#ddd')
    self.profinfomanfmod = tk.Label(self.profinfocont, text='Manufacturer Model:', highlightbackground='#ddd', bg='#ddd')
    self.profinfoinst = tk.Label(self.profinfocont, text='Institution Name:', highlightbackground='#ddd', bg='#ddd')
    self.profhomogname = tk.Label(self.profinfocont, text='Homogeneity \nSlice Location:', highlightbackground='#ddd', bg='#ddd')
    self.profupperlimit = tk.Label(self.profinfocont, text='Upper Homogeneity Limit:', highlightbackground='#ddd', bg='#ddd')
    self.proflowerlimit = tk.Label(self.profinfocont, text='Lower Homogeneity Limit:', highlightbackground='#ddd', bg='#ddd')

    # Label placement
    self.profinfoname.grid(column=0, row=0, stick='e', padx=(0,10))
    self.profinfomanf.grid(column=0, row=1, stick='e', padx=(0,10))
    self.profinfomanfmod.grid(column=0, row=2, stick='e', padx=(0,10))
    self.profinfoinst.grid(column=0, row=3, stick='e', padx=(0,10))
    self.profhomogname.grid(column=0, row=4, stick='e', padx=(0,10))
    self.profupperlimit.grid(column=0, row=5, stick='e', padx=(0,10))
    self.proflowerlimit.grid(column=0, row=6, stick='e', padx=(0,10))

    # Data Entry
    self.profentryname = tk.Entry(self.profinfocont, width=35)
    self.profcombo = ttk.Combobox(self.profinfocont, width=35)
    self.profentrymanfmod = tk.Entry(self.profinfocont, width=35)
    self.profentryinst = tk.Entry(self.profinfocont, width=35)
    self.profentryhomog = tk.Entry(self.profinfocont, width=35)
    self.profentryupper = tk.Entry(self.profinfocont, width=35)
    self.profentrylower = tk.Entry(self.profinfocont, width=35)

    # Data entry placement
    self.profentryname.grid(column=1, row=0, sticky='w')
    self.profcombo.grid(column=1, row=1, sticky='w')
    self.profentrymanfmod.grid(column=1, row=2, sticky='w')
    self.profentryinst.grid(column=1, row=3, sticky='w')
    self.profentryhomog.grid(column=1, row=4, sticky='w')
    self.profentryupper.grid(column=1, row=5, sticky='w')
    self.profentrylower.grid(column=1, row=6, sticky='w')

    # Populating data entry
    self.profentryname.insert(0, profile['StationName'])
    self.profentrymanfmod.insert(0, profile['ManufacturerModelName'])
    self.profentryinst.insert(0, profile['InstitutionName'])
    self.profentryhomog.insert(0, profile['HomogeneityPosition'])
    self.profentryupper.insert(0, profile['UpperHomogeneityLimit'])
    self.profentrylower.insert(0, profile['LowerHomogeneityLimit'])

    # Manufacturer combo box setup
    self.profcombo['values'] = profileutil.MANF_LIST # Load list of a valid manf options
    self.profcombo['state'] = 'readonly'
    # If the profile's manfacturer info is in the list, set combobox to it
    if profile['Manufacturer'] in profileutil.MANF_LIST:
      self.profcombo.set(profile['Manufacturer'])
    else:
      self.profcombo.set('Select a manfacturer...')
    self.profcombo.bind('<<ComboboxSelected>>', lambda event: self.component_change('Manufacturer', self.profcombo.get(), id)) # Save and update components on change

    # Binding data entry to component_change
    self.profentryname.bind("<KeyRelease>", lambda event: self.component_change("StationName", self.profentryname.get(), id))
    self.profentrymanfmod.bind("<KeyRelease>", lambda event: self.component_change("ManufacturerModelName", self.profentrymanfmod.get(), id))
    self.profentryinst.bind("<KeyRelease>", lambda event: self.component_change("InstitutionName", self.profentryinst.get(), id))
    self.profentryhomog.bind("<KeyRelease>", lambda event: self.component_change("HomogeneityPosition", self.profentryhomog.get(), id))
    self.profentryupper.bind("<KeyRelease>", lambda event: self.component_change("UpperHomogeneityLimit", self.profentryupper.get(), id))
    self.profentrylower.bind("<KeyRelease>", lambda event: self.component_change("LowerHomogeneityLimit", self.profentrylower.get(), id))

    # Row and Column weights
    self.profinfocont.grid_columnconfigure(0, weight=2)
    self.profinfocont.grid_columnconfigure(1, weight=3)
    self.profinfocont.grid_rowconfigure(0, weight=1)
    self.profinfocont.grid_rowconfigure(1, weight=1)
    self.profinfocont.grid_rowconfigure(2, weight=1)
    self.profinfocont.grid_rowconfigure(3, weight=1)
    self.profinfocont.grid_rowconfigure(4, weight=1)
    self.profinfocont.grid_rowconfigure(5, weight=1)
    self.profinfocont.grid_rowconfigure(6, weight=1)


  def component_change(self, comp, val, profid, baseline=False):
    # Parsing input from homog/linearity
    self.changes_made()
    if comp in ['HomogeneityPosition', 'LinearityPosition', 'UpperHomogeneityLimit', 'LowerHomogeneityLimit']:
      try:
        val = int(val)
      except ValueError:
        return
    
    if self.profiles.get(profid):
      # Updating current profile value
      if baseline:
        try:
          self.profiles[profid]['Baseline'][comp] = float(val)
        except ValueError:
          pass
      else:
        self.profiles[profid][comp] = val
      self.profilesChanged = True
    elif self.profilesToAdd.get(profid):
      if baseline:
        try:
          self.profilesToAdd[profid]['Baseline'][comp] = float(val)
        except ValueError:
          pass
      else:
        self.profilesToAdd[profid][comp] = val
    else:
      print('Profile with id: %s could not be found' % profid)
      return -1


  def auto_profiles(self):
    # Asking if the user wishes to download all images from source
    size = autoprofiles.getSize()
    if size > 0:
      msg = '''Auto finding CT profiles will download %s MB of images and clear any unsaved, manually entered profiles.
      \n Are you sure you wish to continue?''' % size
      self.parent.update() # Ensuring messagebox works on mac
      userchoice = messagebox.askyesno("Image Download", msg, parent=self.parent)

      # If the user agrees
      if userchoice:
        # Showing progress bar
        self.auto_profiles_progress = tk.Toplevel(master=self.parent)
        self.auto_profiles_progress.geometry('250x100')
        self.auto_profiles_title = tk.LabelFrame(self.auto_profiles_progress, text='Finding Profiles')
        self.auto_profiles_title.pack(expand=True, fill='both', padx=15, pady=10)
        self.progress = ttk.Progressbar(self.auto_profiles_title, orient='horizontal', length=200, mode='indeterminate')
        self.progress.pack(expand=True)
        self.progress.start()

        # Defining auto profile function to run on a thread
        def run_auto(cleanup):
          # Running auto profiler
          autoprofiles.run()
          # Cleaning up
          cleanup()

        def cleanup():
          # Re-opening profiles.json with new profiles
          self.profiles = profileutil.openProfiles(self.profilepath)

          # Reloading the profile client
          self.proflist.canvas.destroy()
          self.proflist.interior.destroy()
          self.proflist.destroy()
          self.mainframe.destroy()
          self.buttonframe.destroy()
          self.load_components()

          #Destroying progress bar
          self.auto_profiles_progress.destroy()
        
        # Running auto profiler on thread
        thread = threading.Thread(target=run_auto, args=(cleanup,))
        thread.start()
    else:
      msg = '''Invalid configuration profile. The utility was unable to check for images to download from the source.
      \n Please check the configuration for valid values and attempt to auto find again.'''
      self.parent.update()
      messagebox.showerror('Auto Find Error', msg, parent=self.parent)


  def manual_profiles(self):
    self.mainframe.destroy()
    self.buttonframe.destroy()
    self.load_components()


  def add_profile(self):
    # Adding new profile under a temp key to the select list
    self.proflist.add('Station Name', 'Manufacturer', self.tempid)

    # Adding new temp profile key to profilesToAdd dict
    self.profilesToAdd[self.tempid] = profileutil.getDefaultProfile()
    self.display_info(self.tempid)
    
    # Selecting newly created profile
    self.proflist.select_element(self.tempid)

    # Incrementing key for next profile
    self.tempid += 1

    #Enabling the save button since we made changes
    self.changes_made()


  def remove_profile(self):
    # Popping from profilesToAdd in case it was a new profile
    # Will return none if it's an existing profile
    wasNewProfile = self.profilesToAdd.pop(self.proflist.selected, False)

    # If the profile was not in profilesToAdd, the key exists in the profiles.json
    # file, thus, we need to delete it from there as well. We delete the profile dict
    # and will save the profile dict back to profiles.json on save
    if not wasNewProfile:
      self.profiles.pop(self.proflist.selected, False)
    
    # Removing profile from list
    self.proflist.remove_selected()
    # Enabling saving
    self.changes_made()

    # Clearing profile info frame, if it exists
    if self.profinfocont.winfo_exists:
      self.profinfocont.destroy()


  def changes_made(self):
    self.savebutton.configure(state=tk.NORMAL)


  def save_profiles(self):
    # If a profile change has been made, iterate through profiles
    # and check that the key is the sum of the attributes
    if self.profilesChanged:
      for key in self.profiles.keys():
        currentName = profileutil.getProfileName(self.profiles.get(key))
        if currentName != key and isinstance(currentName, str):
          tempProfile = self.profiles.get(key)
          self.profiles.pop(key, None)
          self.profiles[currentName] = tempProfile
          print('Key change detected')

    # Merging new profiles with current profiles
    if len(self.profilesToAdd) > 0:
      # Validating and saving profiles
      for key in self.profilesToAdd.keys():
        profile = self.profilesToAdd[key]
        # Checking that profile is valid
        res = profileutil.validProfile(profile)
        if res:
          # If so, we make the id from the attrbs
          id = (
            profile['StationName']+'-'+
            profile['Manufacturer'].upper()+'-'+
            profile['ManufacturerModelName'].upper()+'-'+
            profile['InstitutionName'].upper()
          )
          # Assign to own field in the profiles dict
          self.profiles[id] = profile
        else:
          self.parent.update()
          messagebox.showerror('Save Error', 'Could not save profiles. An error occured during ' +
            'the save. \nPlease make sure all profile fields are filled in. \nConsult '+
            'the log for more details.', parent=self.parent)
          return
    # Resetting profilesToAdd
    self.profilesToAdd = {}
    
    # Saving profiles
    profileutil.saveProfiles(self.profilepath, self.profiles)
    # Reload components panel due to self.profiles update
    self.mainframe.destroy()
    self.buttonframe.destroy()
    self.load_components()
    # Disable save button
    self.savebutton.configure(state=tk.DISABLED)


  def add_placeholder_to(self, entry, placeholder, color="grey", font=None):
    normal_color = entry.cget("fg")
    normal_font = entry.cget("font")
    
    if font is None:
      font = normal_font

    state = Placeholder_State()
    state.normal_color=normal_color
    state.normal_font=normal_font
    state.placeholder_color=color
    state.placeholder_font=font
    state.placeholder_text = placeholder
    state.with_placeholder=True

    def on_focusin(event, entry=entry, state=state):
      if state.with_placeholder:
        entry.delete(0, "end")
        entry.config(fg = state.normal_color, font=state.normal_font)
    
        state.with_placeholder = False

    def on_focusout(event, entry=entry, state=state):
      if entry.get() == '':
        entry.insert(0, state.placeholder_text)
        entry.config(fg = state.placeholder_color, font=state.placeholder_font)
        
        state.with_placeholder = True

    entry.insert(0, placeholder)
    entry.config(fg = color, font=font)

    entry.bind('<FocusIn>', on_focusin, add="+")
    entry.bind('<FocusOut>', on_focusout, add="+")
    
    entry.placeholder_state = state

    return state



  def exit_client(self):
    if self.firstrun:
      self.parent.quit()
    else:
      self.parent.destroy()

  
  def save_and_quit(self):
    self.save_profiles()
    self.exit_client()


class Placeholder_State(object):
  __slots__ = 'normal_color', 'normal_font', 'placeholder_text', 'placeholder_color', 'placeholder_font', 'with_placeholder'
