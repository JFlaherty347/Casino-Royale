import pygame, tkinter

#Track selection
track_name_list = ("R/B", 'G/S', 'R/S', 'D/P')
track_list = ("GS_GameCorner.mp3", "GS_GameCorner.mp3", "RS_GameCorner.mp3", "DP_GameCorner.mp3")
current_track = 0

pygame.mixer.init()
pygame.mixer.music.load(track_list[current_track])
pygame.mixer.music.play()

def incrementTrack():
    global current_track
    current_track = (current_track + 1) % len(track_list)
    track_name.config(text = track_name_list[current_track])
    
    #Change to new track
    pygame.mixer.music.stop()
    #pygame.mixer.music.unload()
    pygame.mixer.music.load(track_list[current_track])
    pygame.mixer.music.play()



def decrementTrack():
    global current_track
    current_track = abs(current_track - 1) % len(track_list)
    track_name.config(text = track_name_list[current_track])

    #Change to new track
    pygame.mixer.music.stop()
    #pygame.mixer.music.unload()
    pygame.mixer.music.load(track_list[current_track])
    pygame.mixer.music.play()

#Exit sequence for program
def exitSeq():
    #Stop Music
    pygame.mixer.music.stop()

    #Destroy master window
    m.destroy()

m = tkinter.Tk()
m.geometry('300x200')
m.title("Casino Royale")
welcome_message = tkinter.Label(m, text = 'Welcome to Casino Royale!', font = ("Calibri", 12))
welcome_message.pack()

topFrame = tkinter.Frame(m)
topFrame.pack()


bottomFrame = tkinter.Frame()
bottomFrame.pack(pady = 25)

trackFrame = tkinter.Frame(m)

trackFrame.pack(side = tkinter.BOTTOM)

#Track select
previous_track_button = tkinter.Button(trackFrame, text ="Previous Track", width = 10, command = decrementTrack)
previous_track_button.grid(row = 0, column = 5)

track_name = tkinter.Label(trackFrame, text = track_name_list[current_track])
track_name.grid(row = 0, column = 6)

next_track_button = tkinter.Button(trackFrame, text = "Next Track", width = 10, command = incrementTrack)
next_track_button.grid(row = 0, column = 7)




horse_race_button = tkinter.Button(topFrame, text = 'Horse Race', width = 10)
horse_race_button.grid(row = 5, column = 4)

blackjack_button = tkinter.Button(topFrame, text = 'Blackjack', width = 10)
blackjack_button.grid(row = 5, column = 5)

quit_button = tkinter.Button(bottomFrame, text = 'Quit', width = 5, command = exitSeq)
quit_button.pack(side = tkinter.RIGHT)





m.mainloop()
