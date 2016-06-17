import tkinter as tk

UI = tk.Tk()

grid = tk.StringVar()
display = tk.Message(UI, textvariable = grid, font = 'fixedsys')

display.pack()

def update():
    txt = ''
    display = open('display')
    for line in display.readlines():
        txt += str(line)
    grid.set(txt)
    UI.after(1000, update)

update()

UI.mainloop()
