"""
挙動を確認するための何でもファイル
ゲームとは何にも関係ない

"""
import tkinter 
root = tkinter.Tk()
root.geometry("300x200")
root.title("hello world")
frame = tkinter.Frame(root)
frame.pack()



label = tkinter.Label(frame,
    text="""
    こんにちは
    こんにちは
    こんにちは
    こんにちは
    こんにちは
    """,
    width=30, 
    anchor=tkinter.W, 
    justify='left'
)
label.pack()

root.mainloop()
