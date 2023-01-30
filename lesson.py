from tkinter import *

root = Tk()

root.title('Своя игра')
# root.geometry('400x250')


def clicked():
    res = f"{entr.get()}"
    lbl.configure(text=res)


btn2 = Button(root, text='Отправить', width=10, height=4, command=clicked) # кнопка
btn2.grid(column=2, row=1)

lbl = Label(root, text='', bd=10, bg='#ffaaaa', font=("Arial Bold", 50)) # метка
lbl.grid(column=2, row=0)

entr = Entry(root,) # текстовое поле
entr.grid(column=0, row=1)




def radios(one, two, three):
    selected = IntVar()
    def my_input():
        if selected.get() == 1:
            lbl.configure(text=one)
        if selected.get() == 2:
            lbl.configure(text=two)
        if selected.get() == 3:
            lbl.configure(text=three)
    rad1 = Radiobutton(root, text=one, value=1, variable=selected)
    rad2 = Radiobutton(root, text=two, value=2, variable=selected)
    rad3 = Radiobutton(root, text=three, value=3, variable=selected)
    btn = Button(root, text='Отправить', width=10, height=4, command=my_input) # кнопка
    btn.grid(column=1, row=5)
    rad1.grid(column=0, row=4)
    rad2.grid(column=1, row=4)
    rad3.grid(column=2, row=4)

radios('Первый вариант', 'Второй вариант', 'Третий вариант')

txt = Text(root, )
txt.grid(column=5, row=5)

# scrollbar = Scrollbar(root, )
# scrollbar.grid(column=2, row=2)


root.mainloop()
