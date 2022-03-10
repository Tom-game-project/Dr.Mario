"""
# Dr.Mario

title : Dr.Mario
mail  : tom.ipynb@gmail.com

Copyright © 2021 tom0427. All rights reserved.
"""

import tkinter
from tkinter import ttk
import os
import logging
import datetime
import random

from enum import Enum

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s- %(message)s"
)

#logging.disable(level=logging.DEBUG)

#Error
class DrMarioError(BaseException,Enum):
    """
    classname:DrMarioError
    description:DrMarioのError
    """
    #Error level
    COLOR:int=0
    OUT_OF_BOTTLE_RANGE:int=1

    #初期化
    def __init__(self,level:int):
        self.level:int = level
    def __str__(self):
        if self.level == 0:  # COLOR
            return "指定されたcolorは見つかりませんでした"
        elif self.level == 1:  # OUT_OF_BOTTLE_RANGE
            return "指定された座標がbottle範囲外です"
        else:
            return "なんかわからんけどerror"

class DrMario(tkinter.Canvas):
    """
    classname:DrMario
    description:game のメインエンジン
    """
    NONE:int = 0  #NONE
    RED:int = 1   #red
    GREEN:int = 2 #green
    BLUE:int = 3  #blue
    def __init__(self,master,*args, **kwargs) -> None:
        super().__init__(master,*args,**kwargs)
        self.master=master
        #images
        self.titleimg = tkinter.PhotoImage(file=os.path.join("image","start","title.png"),format="png")
        self.startimg = tkinter.PhotoImage(file=os.path.join("image","start","start.png"),format="png")
        self.startimg1 = tkinter.PhotoImage(file=os.path.join("image","start","start1.png"),format="png")
        self.count1png = tkinter.PhotoImage(file=os.path.join("image","start","1.png"),format="png")
        self.count2png = tkinter.PhotoImage(file=os.path.join("image","start","2.png"),format="png")
        self.count3png = tkinter.PhotoImage(file=os.path.join("image","start","3.png"),format="png")
        self.blue_block = tkinter.PhotoImage(file=os.path.join("image","game","_blue.png"),format="png")   #image size(50,50)
        self.red_block = tkinter.PhotoImage(file=os.path.join("image","game","_red.png"),format="png")     #image size(50,50)
        self.green_block = tkinter.PhotoImage(file=os.path.join("image","game","_green.png"),format="png") #image size(50,50)
        #create start image
        self.create_image(300, 200, image=self.titleimg,tag="title")
        self.start_button=self.create_image(300, 400, image=self.startimg,tag="start")
        #start button tag付け
        self.tag_bind("start", "<Button-1>",self.start_button_event_push)
        self.tag_bind("start", "<Enter>", self.start_button_event_enter)
        self.tag_bind("start", "<Leave>", self.start_button_event_leave)
        #key bool
        self.set_keys_False()
        #level stage
        self.stage:int = 0
        self.level:int = 0
        #block image size
        self.block_image_size:int = 50 # 画像は正方形であること
        #定数の設定
        #bottle position
        self.bottle_position:tuple[int,int]=(200,50)
        #bottle size
        self.bottle_size:tuple[int,int] = (7,10)
        #bottle の設計
        self.bottle:list[list[int]] = [[0 for j in range(self.bottle_size[0])] for i in range(self.bottle_size[1])]
        #next medicine display
        self.next_medicine_position:tuple[int,int]=(20,50) #next medicineの表示位置
        self.next_medicine_size:tuple[int,int]=(150,100)     #next medicine のsize
        #max block tag
        self.block_max_tag:int = 0
    #start画面インターフェイス
    def start_button_event_push(self,e):
        """
        ボタン押下時の画面遷移
        """
        self.delete("title")
        self.delete("start")
        self.count = [0,datetime.datetime.now()]
        self.create_image(300, 300, image=self.count3png, tags="counter")
        self.after_cancel(self.now_process)
        self.now_process=self.after(0,self.count_loop)
        logging.debug("押下！")
    def start_button_event_enter(self,e):
        #領域内に入った
        self.itemconfig(self.start_button,image=self.startimg1)
        logging.debug("入った")
    def start_button_event_leave(self,e):
        #領域内からでた
        self.itemconfig(self.start_button,image=self.startimg)
        logging.debug("出た")
    #game画面インターフェイス
    #bottleを描画
    def bottle_frame(self,x1, y1, x2, y2, r):
        """
        bottleを描画
        """
        self.create_line(x1, y1+r, x1, y2-r, fill="white",tags="bottle")
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180,extent=90, style=tkinter.ARC, outline="white",tags="bottle")
        self.create_line(x1+r, y2, x2-r, y2, fill="white", tags="bottle")
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270,extent=90, style=tkinter.ARC, outline="white",tags="bottle")
        self.create_line(x2, y2-r, x2, y1+r, fill="white",tags="bottle")
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,extent=90, style=tkinter.ARC, outline="white",tags="bottle")
        self.create_line(x2-r, y1, x1+r, y1, fill="white",tags="bottle")
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,extent=90, style=tkinter.ARC, outline="white",tags="bottle")
    #medicine描画処理
    def create_medicine(self)->tuple:
        """
        薬を作る
        """
        cho:list = [self.RED, self.GREEN, self.BLUE]
        medi: tuple = (random.choice(cho), random.choice(cho))
        return medi
    def color_compile(self,color:int):
        """
        color number からcolor objectを返します
        """
        if color==1:
            return self.red_block
        elif color==2:
            return self.green_block
        elif color==3:
            return self.blue_block
        else:
            raise DrMarioError(DrMarioError.COLOR)
    def set_next_medicine(self)->None:
        """
        次の薬を設定する
        
        """
        self.next_medicine:tuple[int,int]=self.create_medicine()                                               #工事中 image のtag付け
        self.create_image(
            self.next_medicine_position[0]+(self.next_medicine_size[0]/2)-(self.block_image_size/2),
            self.next_medicine_position[1]+(self.next_medicine_size[1]/2),
            image=self.color_compile(self.next_medicine[0]),
            )
        self.create_image(
            self.next_medicine_position[0]+(self.next_medicine_size[0]/2)+(self.block_image_size/2),
            self.next_medicine_position[1]+(self.next_medicine_size[1]/2),
            image=self.color_compile(self.next_medicine[1]),
            )
    def drop_start(self):
        """
        薬の落下を開始する
        """
        pass                                              #工事中
    def drop_medicine(self):
        """
        薬を落とすアニメーション
        """
        pass                                               #工事中
    def next_stage(self):
        """
        今のgameをコンプリートした際に次のステージに進む
        """
        pass                                               #工事中
    #medicine処理
    def put_block(self,x,y,color)->None:
        """
        指定されたbottle上の座標にブロックを置く
        ```python
        self.put_block(5,5,self.RED)
        ```
        """
        if color==1:   # red
            image = self.red_block
        elif color==2: # green
            image = self.green_block
        elif color==3: # blue
            image = self.blue_block
        else:
            raise DrMarioError(DrMarioError.COLOR)
        if not 0<= x <self.bottle_size[0]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        if not 0<= y <self.bottle_size[1]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        self.bottle[y][x]= color
        self.create_image(self.bottle_position[0]+self.block_image_size/2+self.block_image_size*x,      #x
                        self.bottle_position[1]+self.block_image_size/2+self.block_image_size*y,        #y
                        image=image,                                                                    #image
                        tags=f"block"                                                                   #tag
                        )
    def get_block(self,x,y)->str:
        """
        指定されたbottle上の座標のブロックを返す
        """
        if not 0 <= x < self.bottle_size[0]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        if not 0 <= y < self.bottle_size[1]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        colornum:int = self.bottle[y][x]
        if colornum==1:
            return "red"
        elif colornum==2:
            return "green"
        elif colornum==3:
            return "blue"
        else:
            return "NONE"
    #keybboard
    #keyをFalseにset
    def set_keys_False(self):
        """
        ## 全てのキーをFalseにする
        """
        self.key_right: bool = False
        self.key_left : bool = False
        self.key_down : bool = False
        self.key_up : bool = False
    def key_events(self,e) -> None:
        """
        keyを受ける
        """
        if e.keysym == "Right":
            self.key_right: bool = True
            logging.debug("Right")
        if e.keysym == "Left":
            self.key_left: bool = True
            logging.debug("Left")
        if e.keysym == "Up":
            self.key_up: bool = True
            logging.debug("Up")
        if e.keysym == "Down":
            self.key_down: bool = True
            logging.debug("Down")
    #カウントダウンアニメーションからの脱出
    def exit_count(self):
        """
        カウントダウンから抜けた後の処理
        """
        #bottleの描画
        self.bottle_frame(
            self.bottle_position[0], self.bottle_position[1],
            self.bottle_position[0]+self.bottle_size[0]*self.block_image_size,
            self.bottle_position[1] +
            self.bottle_size[1]*self.block_image_size, 10
        )
        self.bottle_frame(
            self.next_medicine_position[0], self.next_medicine_position[1],
            self.next_medicine_position[0]+self.next_medicine_size[0],
            self.next_medicine_position[1]+self.next_medicine_size[1],
            10
        )
        self.after_cancel(self.now_process)
        self.now_process = self.after(0, self.game_loop)
        logging.debug("start!!")                                                 #  こっから game start
        self.set_next_medicine()
        self.put_block(6,9,self.RED)        #試験的なput
        logging.debug(self.get_block(6, 9))  # 試験的なget
    def game_over(self):
        """
        ゲームオーバー時の画面遷移
        """
        self.after_cancel(self.now_process)
        self.now_process=self.after(0,self.result_loop)

    def start_loop(self) -> None:
        """
        ## スタート画面loop
        """
        self.now_process=self.after(10, self.start_loop)
    def count_loop(self):
        """
        カウントダウンアニメーションのloop
        """
        if self.count[0]==0 and datetime.datetime.now()-self.count[1]>=datetime.timedelta(seconds=1):
            self.itemconfig("counter",image=self.count2png)
            self.count[0]=1
        elif self.count[0]==1 and datetime.datetime.now()-self.count[1]>=datetime.timedelta(seconds=2):
            self.itemconfig("counter",image=self.count1png)
            self.count[0]=2
        elif self.count[0]==2 and datetime.datetime.now()-self.count[1]>=datetime.timedelta(seconds=3):
            self.delete("counter")
            self.exit_count()
            return True #確実にloopを殺す
        else:
            pass
        self.now_process=self.after(10, self.count_loop)
    def game_loop(self):
        """
        ## ゲームloop
        """
        self.delete("clock")
        self.set_keys_False() #keyをset
        """
        if self.key_right:
            logging.debug("right")
        if self.key_left:
            logging.debug("left")
        if self.key_down:
            logging.debug("down")
        if self.key_up:
            logging.debug("up")
        """
        
        self.now_process = self.after(10, self.game_loop)
    def result_loop(self):
        """
        リザルト画面loop
        """
        self.now_process = self.after(10, self.result_loop)


if __name__=="__main__":
    root=tkinter.Tk()
    root.title("Dr.Mario")
    frame = ttk.Frame(root)
    frame.pack()
    
    canvas = DrMario(frame,width=600,height=600,bg="black")
    canvas.pack()
    root.bind("<Key>",canvas.key_events)
    
    canvas.after(0,canvas.start_loop)
    
    root.mainloop()