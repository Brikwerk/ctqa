"""
Select List

Contains logic for implementing a list with selection, addition, and deletion functions.
"""

import os, sys, json, platform
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class select_list(tk.Frame):
  """Main Select List class for instantiating the list in a Tkinter frame."""

  def __init__(self, parent, *args, **kw):
    self.items = {}
    self.selectcallbacks = []
    self.selected = None
    self.kw = kw

    tk.Frame.__init__(self, parent, *args, **kw)

    # create a canvas object and a vertical scrollbar for scrolling it
    vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
    vscrollbar.pack(fill='y', side=tk.RIGHT, expand=tk.FALSE)
    canvas = tk.Canvas(self, bd=0, highlightthickness=0, **kw,
                    yscrollcommand=vscrollbar.set)
    self.canvas = canvas
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
    vscrollbar.config(command=canvas.yview)

    # reset the view
    canvas.xview_moveto(0)
    canvas.yview_moveto(0)

    # create a frame inside the canvas which will be scrolled with it
    self.interior = interior = tk.Frame(canvas, **kw)
    interior_id = canvas.create_window(0, 0, window=interior,
                                        anchor=tk.NW)

    def _on_mousewheel(event):
      canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Hack to fix bound scroll behaviour on Mac's variant of tkinter
    if platform.system() != 'Darwin':
      self.bind_id = self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(event):
        # update the scrollbars to match the size of the inner frame
        size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
        canvas.config(scrollregion="0 0 %s %s" % size)
        if interior.winfo_reqwidth() != canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            canvas.config(width=interior.winfo_reqwidth())

    interior.bind('<Configure>', _configure_interior)


    def _configure_canvas(event):
        if interior.winfo_reqwidth() != canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            canvas.itemconfigure(interior_id, width=canvas.winfo_width())

    canvas.bind('<Configure>', _configure_canvas)

    def _destroy(event):
      self.canvas.unbind_all('<MouseWheel>')
      self.canvas.destroy()
      self.interior.destroy()
      self.destroy()

    self.bind('<Destroy>', _destroy)


  def add(self, title, subtitle, id):
    self.items[id] = {}
    # Setting item contents and settings
    self.items[id]['container'] = tk.Frame(self.interior)
    self.items[id]['title'] = tk.Label(self.items[id]['container'],
      text=title,
      justify=tk.LEFT,
      anchor='w',
      width=5)
    self.items[id]['subtitle'] = tk.Label(self.items[id]['container'],
      text=subtitle,
      justify=tk.LEFT,
      anchor='w',
      width=8)

    # Setting labels and frame same color as bg if available
    if self.kw.get('background'):
      self.items[id]['container'].config(
        background=self.kw['background'])
      self.items[id]['title'].config(
        background=self.kw['background'],
        highlightbackground=self.kw['background'])
      self.items[id]['subtitle'].config(
        background=self.kw['background'],
        highlightbackground=self.kw['background'])

    # Packing
    self.items[id]['container'].pack(side='top', fill='x', anchor='w')
    self.items[id]['title'].pack(side='top', anchor='w', fill='x', padx=(10,0), pady=(5,0))
    self.items[id]['subtitle'].pack(side='bottom', fill='x', anchor='w', padx=(10,0), pady=(0,5))

    # Setting font
    self.items[id]['title'].config(font='Helvetica 11 bold')
    self.items[id]['subtitle'].config(font='Helvetica 10 bold', fg='#a2a1a1')

    # Binding select on click to elm
    self.items[id]['container'].bind("<Button-1>", lambda event: self.select_element(id))
    self.items[id]['title'].bind("<Button-1>", lambda event: self.select_element(id))
    self.items[id]['subtitle'].bind("<Button-1>", lambda event: self.select_element(id))

    # Selecting elm if it's the first addition
    if self.selected == None:
      self.selected = id
      self.select_color(id)


  def bind_select_callback(self, callback):
    self.selectcallbacks.append(callback)


  def remove_selected(self):
    if self.selected != None:
      self.items[self.selected]['container'].destroy()
      self.items.pop(self.selected, None)
      self.selected = None


  def select_color(self, id):
    self.items[id]['container'].config(background='#0068d9')
    self.items[id]['title'].config(background='#0068d9', highlightbackground='#0068d9', fg='white')
    self.items[id]['subtitle'].config(background='#0068d9', highlightbackground='#0068d9', fg='white')


  def unselect_color(self, id):
    self.items[id]['container'].config(background='#fff')
    self.items[id]['title'].config(background='#fff', highlightbackground='#fff', fg='black')
    self.items[id]['subtitle'].config(background='#fff', highlightbackground='#fff', fg='#a2a1a1')


  def select_element(self, id):
    if self.selected != None:
      self.unselect_color(self.selected)
    self.selected = id
    self.select_color(id)
    # Call all bound callbacks
    for callback in self.selectcallbacks:
      callback(self.selected)


  def change_id(self, oldid, newid):
    tempItem = self.items[oldid]
    self.items.pop(oldid, None)
    tempItem[newid] = tempItem

    if self.selected == oldid:
      self.selected == newid
    
