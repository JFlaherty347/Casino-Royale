
def update_progress(progress, total):
    percent = round((progress/total)*50)
    string = "\033[1;31m"+"Horse 1: [" +"■"*percent+" "*(50-percent)+"]"
    print(string)

update_progress(15, 20)