#Author: Aaron Jimenez
#Date: Dec 08, 2019
#Runs horse race simulation using multithreading and GUI using the tkinter library

import threading
import random
import time
import pygame, tkinter
from tkinter import ttk
from tkinter import Tk
from collections import deque

finishLine = 50000
finishedHorses = []
horseCompletion = []
horse_progress_bars_queue = deque()
lock = threading.Lock()
#window = tkinter.Tk()
threads = []
playAgain = True
numberOfGamblers = 5
maxHorses = 5

#Class that creates and runs each horse race thread, child of threading.Thread class
class horseRaceThread(threading.Thread):
    def __init__(self, name, horse):
        threading.Thread.__init__(self)
        self.name = name
        self.horse = horse

    def run(self):
        position = 0
        timeFinished = 0
        global finishLine
        global finishedHorses
        global lock
        
        # Keep incrementing position of horse until they reach the finish line
        while position <= finishLine:
            
            newPosition = random.randrange(1, 500)
            position += newPosition
            
            timeFinished += 5

            #Add position and horse to queue
            lock.acquire()
            horse_progress_bars_queue.append((self.horse.horseNumber, position))
            lock.release()

            # Sleep to allow to prevent first thread from always finishing first
            time.sleep(0.01)


        # Get time finished for horse
        horse.finishTime = time


        # Append horse to list of horses finished
        # Set lock to serialize
        lock.acquire()
        finishedHorses.append(self.horse)
        self.horse.setFinish(timeFinish=timeFinished)
        self.horse.printHorse()
        lock.release()

#Class that creates each horse
#Contains the horse's ID number, their max speed, and at what time they finished
class horse():
    def __init__(self, horseNumber, maxSpeed):
        self.horseNumber = horseNumber
        self.maxSpeed = maxSpeed
        self.finishTime = 0

    def printHorse(self):
        print("Horse %d finished at time %4d" % (self.horseNumber, self.finishTime))

    def setFinish(self, timeFinish):
        self.finishTime = timeFinish

#Class that creates each gambler
#Contains their name, gambler ID number, their current amount of money, and which horse they are currently betting on
class gambler():
    def __init__(self, gamblerName, maxHorses, currentAmountOfMoney):
        self.gamblerName = gamblerName
        self.horseBet = random.randrange(1, maxHorses + 1)
        self.cash = currentAmountOfMoney
        self.bet = random.randrange(1, self.cash + 1)
        self.gamblerID = self.gamblerIDGen()

    def wonBet(self):
        self.cash += self.bet

    def lostBet(self):
        self.cash -= self.bet
    
    def gamblerIDGen(self):
        return str(hex(random.randrange(0, 1100) * 5678978))[2:]


#Initializes and prepares for simulation
def horseRun():
    """ pygame.mixer.init()
    pygame.mixer.music.load("gameCorner.mp3")
    pygame.mixer.music.play() """

    global playAgain
    global threads
    global finishedHorses
    global numberOfGamblers
    global maxHorses

    
    threads.clear()
    finishedHorses.clear()
    horseCompletion.clear()
    horse_progress_bars_queue.clear()

    #Create gamblers
    gamblers = []
    for i in range(1, numberOfGamblers + 1):
        gamblers.append(gambler(i, maxHorses, currentAmountOfMoney=random.randrange(1, 151)))

    

    #Create GUI for horse race
    window = tkinter.Toplevel(width = 500)
    window.title("Horse Race")

    
   


    #Create dialogue frame
    dialogue_frame = tkinter.Frame(window)
    dialogue_frame.pack(side = tkinter.RIGHT, pady = 15)

    #create scrollbar
    scrollbar_result_list = tkinter.Scrollbar(dialogue_frame)
    scrollbar_result_list.pack(side = tkinter.RIGHT, fill = tkinter.Y)

    #create dialogue listbox
    dialogue_listbox = tkinter.Listbox(dialogue_frame, width = 30)
    dialogue_listbox.pack(side = tkinter.LEFT)

    #Print Receipt menu bar
    menu = tkinter.Menu(window)
    window.config(menu = menu)

    fileMenu = tkinter.Menu(menu)
    menu.add_cascade(label = "File", menu = fileMenu)



    receipt_print = lambda : printReciept(gamblers)
    fileMenu.add_command(label = "Print Reciept", command = receipt_print)
    fileMenu.add_command(label = "Quit", command = window.destroy)


    



    #progress bar frame
    progress_bar_frame = tkinter.Frame(window)
    progress_bar_frame.pack(side = tkinter.LEFT, pady = 15)

    horse_progress_bar = []
    #create progress bars
    for i in range(0, maxHorses):
        horse_and_bar = (tkinter.Label(progress_bar_frame, text = 'Horse '+str(i + 1)+": "), ttk.Progressbar(progress_bar_frame, orient = tkinter.HORIZONTAL, length = 100, maximum = finishLine, mode = 'determinate'))
        horse_and_bar[0].pack()
        horse_and_bar[1].pack()
        horse_progress_bar.append(horse_and_bar)
    
    step_horse = lambda : step(gamblers, window, horse_progress_bar, dialogue_listbox)

    #Create run button
    tkinter.Button(progress_bar_frame, text = "RUN", command = step_horse).pack()
    tkinter.Button(progress_bar_frame,text = "DONE", command = window.destroy).pack()

    window.mainloop()

    print("\t\tEND HORSE RACE")

#Prints the receipt of every gambler to file located in the receipts folder
def printReciept(gamblers):
    gamblerRecieptName = list("../Receipts/PlayerXReciept.txt")

    for player in gamblers:
       gamblerRecieptName[18] = str(player.gamblerName)
       
       newfile = open("".join(gamblerRecieptName), "w")
       print(("🍙"*20)+"Player ID: %s" %player.gamblerID + ("🍙"*20), file = newfile)
       print(("\t"*10)+"Total Player Credits $%d" %player.cash, file = newfile)
       print(("\n"*15)+"\t"*5+"\u00A9 Casino Royale\u2122 Enterprises", file = newfile)
       newfile.close()

#Runs the simulation of the horse race using the queue of the positions of each horse that was generated using multithreading
def step(gamblers, window, horse_progress_bar, dialogue_listbox):
    
    #Initialize all vars to default state
    threads.clear()
    finishedHorses.clear()

    # Create horses and threads
    for i in range(1, maxHorses + 1):
        #horseCompletion.extend([" ", " ", " ", " ", " "])
        threads.append(horseRaceThread(name=i, horse=horse(horseNumber=i, maxSpeed=random.randrange(13, 18))))
    
    # Start threads
    for x in threads:
        x.start()

        # Join threads
    for x in threads:
        x.join()

    #Simulate horse race
    while (len(horse_progress_bars_queue) > 0):
        x = horse_progress_bars_queue.popleft()
        if (x[1] >= finishLine):
            horse_progress_bar[x[0]-1][1]['value'] = finishLine
        else:
            horse_progress_bar[x[0]-1][1]['value'] = x[1]
        window.update_idletasks()
        time.sleep(.008)
        
    #Print horses
    dialogue_listbox.insert(tkinter.END, (("*"*5) + "Race Results" + ("*"*5)))
    for race_horse in finishedHorses:
        dialogue_listbox.insert(tkinter.END, (" "*5) + ("Horse %d finished at time %d" %(race_horse.horseNumber, race_horse.finishTime)))
        time.sleep(0.1)


    # print which horse won
    dialogue_listbox.insert(tkinter.END, "")
    dialogue_listbox.insert(tkinter.END, ("Winner: Horse %d" % finishedHorses[0].horseNumber))
    dialogue_listbox.insert(tkinter.END, "")
        

    # Check who won
    for gamble in gamblers:
        if gamble.horseBet == finishedHorses[0].horseNumber:
            #print("Player %d Has Won $%d:" % (gamble.gamblerName, gamble.bet))
            dialogue_listbox.insert(tkinter.END, ("Player %d Has Won $%d:" % (gamble.gamblerName, gamble.bet)))
            gamble.wonBet()
        else:
            #print("Player %d Has Lost $%d:" % (gamble.gamblerName, gamble.bet))
            dialogue_listbox.insert(tkinter.END, ("Player %d Has Lost $%d:" % (gamble.gamblerName, gamble.bet)))
            gamble.lostBet()

        #print("\tCurrent Credits: $%d" % gamble.cash)
        dialogue_listbox.insert(tkinter.END, (" "*5+"Current Credits: $%d" % gamble.cash))
    

        




#horseRun()
