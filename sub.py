"""
挙動を確認するための何でもファイル
ゲームとは何にも関係ない
mouse wheel 動作
"""
import tkinter
import platform

root = tkinter.Tk()


current_os = platform.system()


def mousewheelevent(e) -> None:
    if current_os == "Windows":
        #一ステップがosによって違う
        print(e.delta/120)
    else:
        print(e.delta)


canvas = tkinter.Canvas()
canvas.pack()

root.bind("<MouseWheel>", mousewheelevent)


root.mainloop()
