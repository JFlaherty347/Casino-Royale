import tkinter, threading
import time
from tkinter import ttk

class addThread(threading.Thread):
    def __init__(self, threadNum):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
    def run(self):
        print("Hello")
        window1 = tkinter.Tk()
        progressBar1 = ttk.Progressbar(window1, orient = tkinter.HORIZONTAL, length = 400, maximum = 500, mode = 'determinate')
        progressBar1.pack()
        for i in range(0, 11):
            progressBar1.step(amount= 10)


def runner():
    t0 = addThread(threadNum= 0)
    t1 = addThread(threadNum= 1)

    t0.start()
    t1.start()

    t0.join()
    t1.join()