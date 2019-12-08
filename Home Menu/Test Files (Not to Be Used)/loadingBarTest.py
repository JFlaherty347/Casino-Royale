import tkinter, threading
import time
from tkinter import ttk
import runner
m = tkinter.Tk()
progressBar = []
progressBar.append(ttk.Progressbar(m, orient = tkinter.HORIZONTAL, length = 400, maximum = 500, mode = 'determinate')) 
progressBar[0].pack()

lock = threading.Lock()

progressBar.append(ttk.Progressbar(m, orient = tkinter.HORIZONTAL, length = 400, maximum = 500, mode = 'determinate')) 
progressBar[1].pack()
def add(threadNum):
    progressBar[threadNum].step(amount = 10)



tkinter.Button(m, text = 'run', command = runner.runner()).pack()
m.mainloop()
