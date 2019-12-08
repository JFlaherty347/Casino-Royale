import tkinter

def newWindow():
    top = tkinter.Toplevel()
    button_home_quit_top = tkinter.Button(top, text = "Quit", command = top.destroy)
    button_home_quit_top.pack()

home = tkinter.Tk()
button_home = tkinter.Button(home, text = "New Window", width = 10, command = newWindow)
button_home_quit = tkinter.Button(home, text = "Quit", command = home.destroy)

button_home.pack()
button_home_quit.pack()

home.mainloop()

