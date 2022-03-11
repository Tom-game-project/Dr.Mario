"""
挙動を確認するための何でもファイル
ゲームとは何にも関係ない
mouse wheel 動作
"""
import tkinter


root = tkinter.Tk()

root.title("moveTo")
frame = tkinter.Frame(root,background="black")
frame.pack(expand=True,fill=tkinter.BOTH)


canvas = tkinter.Canvas(frame)
canvas.pack()

image = tkinter.PhotoImage(file="image\game\_blue.png")


canvas.create_image(10,10,image=image,tags="image")
canvas.moveto("image",0 ,0)



root.mainloop()
