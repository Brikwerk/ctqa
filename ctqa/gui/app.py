import tkinter as tk
from . import client as client


def run():
  """Runs main CTQA Tkinter GUI"""
  root = tk.Tk()
  client.ctqa_client(root)
  root.mainloop()


if __name__ == '__main__':
  run()
