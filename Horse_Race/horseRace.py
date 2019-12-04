import threading
import random
import time
import pygame

finishLine = 500000
finishedHorses = []
horseCompletion = []

def updateHorseCompletion(horseNumber, position):
    index = round((position/finishLine))


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
        global initialTime
        # Keep incrementing position of horse until they reach the finish line
        while position <= finishLine:
            position += random.randrange(1, 500)
            # print(position)
            timeFinished += 5
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


class horse():
    def __init__(self, horseNumber, maxSpeed):
        self.horseNumber = horseNumber
        self.maxSpeed = maxSpeed
        self.finishTime = 0

    def printHorse(self):
        print("Horse %d finished at time %4d" % (self.horseNumber, self.finishTime))

    def setFinish(self, timeFinish):
        self.finishTime = timeFinish


class gambler():
    def __init__(self, gamblerName, maxHorses, currentAmountOfMoney):
        self.gamblerName = gamblerName
        self.horseBet = random.randrange(1, maxHorses + 1)
        self.cash = currentAmountOfMoney
        self.bet = random.randrange(1, self.cash + 1)

    def wonBet(self):
        self.cash += self.bet

    def lostBet(self):
        self.cash -= self.bet


if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load("gameCorner.mp3")
    pygame.mixer.music.play()

    playAgain = True

    while playAgain:
        lock = threading.Lock()
        gamblers = []
        numberOfGamblers = 5
        maxHorses = 5
        threads = []


        # Create gamblers
        for i in range(1, numberOfGamblers + 1):
            gamblers.append(gambler(i, maxHorses, currentAmountOfMoney=random.randrange(1, 151)))

        # Create horses and threads
        for i in range(1, maxHorses + 1):
            horseCompletion.append([" ", " ", " ", " ", " "])
            threads.append(horseRaceThread(name=i, horse=horse(horseNumber=i, maxSpeed=random.randrange(13, 18))))

        # Start threads
        for x in threads:
            x.start()

        # Join threads
        for x in threads:
            x.join()

        # print which horse won
        # global finishedHorses
        print("\nWinner: Horse %d\n" % finishedHorses[0].horseNumber)

        # Check who won
        for gamble in gamblers:
            if gamble.horseBet == finishedHorses[0].horseNumber:
                print("Player %d Has Won $%d:" % (gamble.gamblerName, gamble.bet))
                gamble.wonBet()
            else:
                print("Player %d Has Lost $%d:" % (gamble.gamblerName, gamble.bet))
                gamble.lostBet()

            print("\tCurrent Credits: $%d" % gamble.cash)

        finishedHorses = []
        userInput = input("Play Again?(Y/N): ")
        playAgain = (userInput.upper() == "Y")

    pygame.mixer.fadeout(5000)
