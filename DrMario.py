"""
# Dr.Mario

title : Dr.Mario
mail  : tom.ipynb@gmail.com

Copyright © 2021 tom0427. All rights reserved.
"""

#だいぶ汚れてるので一通り書き終えたら整える

import tkinter
from tkinter import ttk
import os
import logging
import datetime
import random

from enum import Enum
from turtle import color
from urllib.parse import ParseResultBytes

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
    OUT_OF_DIRECTION_RANGE:int=2

    #初期化
    def __init__(self,level:int):
        self.level:int = level
    def __str__(self):
        if self.level == 0:  # COLOR
            return "指定されたcolorは見つかりませんでした"
        elif self.level == 1:  # OUT_OF_BOTTLE_RANGE
            return "指定された座標がbottle範囲外です"
        elif self.level == 2:  # OUT_OF_DIRECTION_RANGE
            return "指定されたangleが範囲外です"
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
        #block angle
        self.angle:int = 0
        #一応宣言だけ
        self.block_x:int
        self.block_y:int
        #定数の設定
        #bottle position
        self.bottle_position:tuple[int,int]=(200,50)
        #bottle size
        self.bottle_size:tuple[int,int] = (7,10)
        #bottle の設計
        self.bottle:list[list[int]] = [[(0,0) for j in range(self.bottle_size[0])] for i in range(self.bottle_size[1])]
        #next medicine display
        self.next_medicine_position:tuple[int,int]=(20,50) #next medicineの表示位置
        self.next_medicine_size:tuple[int,int]=(150,100)     #next medicine のsize
        #drop speed の設定
        self.drop_speed:int = 5
        #落ち始めたところからのピクセル単位の距離
        self.drop_position:int = 0
        self.odd_block_color:int
        self.even_block_color:int
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
    def num_to_color_obj(self,color:int):
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
    def num_to_color(self, color: int) -> int:
        """
        color number からcolorを返す
        """
        if color == 1:
            return "red"
        elif color==2:
            return "green"
        elif color==3:
            return "blue"
        elif color==0:
            return "NONE"
        else:
            logging.debug(color)
            raise DrMarioError(DrMarioError.COLOR)
    def set_next_medicine(self,block_max_tag:int)->None:
        """
        次の薬を設定する
        
        """
        self.next_medicine:tuple[int,int]=self.create_medicine()                                               #工事中 image のtag付け
        self.create_image(
            self.next_medicine_position[0]+(self.next_medicine_size[0]/2)-(self.block_image_size/2),
            self.next_medicine_position[1]+(self.next_medicine_size[1]/2),
            image=self.num_to_color_obj(self.next_medicine[0]),
            tags=f"block:{block_max_tag+1}"
        )
        self.create_image(
            self.next_medicine_position[0]+(self.next_medicine_size[0]/2)+(self.block_image_size/2),
            self.next_medicine_position[1]+(self.next_medicine_size[1]/2),
            image=self.num_to_color_obj(self.next_medicine[1]),
            tags=f"block:{block_max_tag+2}"
        )
    def drop_start(self):
        """
        薬の落下を開始する
        待機スペースから薬を移動させてくる
        """
        self.angle:int = 2
        self.block_x:int = int(self.bottle_size[0]/2)
        self.block_y:int = 0
        self.drop_position: int = 0
        self.odd_block_color:int = self.next_medicine[0]
        self.even_block_color:int= self.next_medicine[1]
        self.put_block(self.block_max_tag-1,int(self.bottle_size[0]/2)-1,0)
        self.put_block(self.block_max_tag,int(self.bottle_size[0]/2),0)
    def drop_medicine(self)->None:
        """
        薬を落とすアニメーション
        """
        if self.key_right:
            #angleが0,2の時右側のblockが地面（ボトル壁面）または他のblockにぶつかったら戻す
            sx:int = 1
            if self.angle==0:
                kind_of_block = self.get_block(self.block_x+2, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            if self.angle==2:
                kind_of_block = self.get_block(self.block_x+1, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            if self.angle==1:
                kind_of_block = self.get_block(self.block_x+1,self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
                kind_of_block = self.get_block(self.block_x+1,self.block_y-1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            if self.angle==3:
                kind_of_block = self.get_block(self.block_x+1,self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
                kind_of_block = self.get_block(self.block_x+1,self.block_y+1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            self.block_x+=sx
            self.move(f"block:{self.block_max_tag-1}",sx*self.block_image_size,0)
            self.move(f"block:{self.block_max_tag}",sx*self.block_image_size,0)
            logging.debug("right")
        if self.key_left:
            #angleが1,3の時右側のblockが地面（ボトル壁面）または他のblockにぶつかったら戻す
            sx: int = -1
            if self.angle==0:
                kind_of_block = self.get_block(self.block_x-1, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            if self.angle==2:
                kind_of_block = self.get_block(self.block_x-2, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int=0
            if self.angle == 1:
                kind_of_block = self.get_block(self.block_x-1, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx: int = 0
                kind_of_block = self.get_block(self.block_x-1, self.block_y-1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx: int = 0
            if self.angle == 3:
                kind_of_block = self.get_block(self.block_x-1, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx: int = 0
                kind_of_block = self.get_block(self.block_x-1, self.block_y+1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    sx:int = 0
            self.block_x+=sx
            self.move(f"block:{self.block_max_tag-1}",sx*self.block_image_size,0)
            self.move(f"block:{self.block_max_tag}",sx*self.block_image_size,0)
            logging.debug("left")
        if self.key_down:
            self.drop_position+=self.drop_speed
            self.block_y = int(self.drop_position/self.block_image_size)
            # angleが 1,3 の時
            # 一番下あるblockが地面又は他のblockにぶつかったら戻す
            if self.angle==1:
                kind_of_block=self.get_block(self.block_x,self.block_y+1)
                if kind_of_block is False or not(kind_of_block=="NONE"):
                    self.landing()
                    return True
            if self.angle==3:
                kind_of_block = self.get_block(self.block_x, self.block_y+2)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    self.landing()
                    return True
            # angleが 0,2 の時
            # 二つのblockのどちらかが地面又は他のblockにぶつかったら戻す
            if self.angle==0:
                kind_of_block = self.get_block(self.block_x, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    self.landing()
                    return True
                kind_of_block = self.get_block(self.block_x+1, self.block_y)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    self.landing()
                    return True
            if self.angle==2:
                kind_of_block = self.get_block(self.block_x, self.block_y+1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    self.landing()
                    return True
                kind_of_block = self.get_block(self.block_x-1, self.block_y+1)
                if kind_of_block is False or not(kind_of_block == "NONE"):
                    self.landing()
                    return True
            self.move(f"block:{self.block_max_tag-1}", 0, self.drop_speed)
            self.move(f"block:{self.block_max_tag}", 0, self.drop_speed)  # 基準
        if self.key_up:
            self.angle = (self.angle+1)%4
            logging.debug(self.block_y)
            if self.change_angle(self.angle):
                pass
            else:
                self.angle = (self.angle-1) % 4
    def compass(self,angle:int)->tuple:
        if angle == 0:
            return (1,0) 
        elif angle==1:
            return (0,-1)
        elif angle==2:
            return (-1,0)
        elif angle==3:
            return (0,1)
        else:
            raise DrMarioError(DrMarioError.OUT_OF_DIRECTION_RANGE)#error送出
    def change_angle(self,angle)->bool:
        next_position:tuple=self.compass(angle)
        status=self.get_block(self.block_x+next_position[0],self.block_y+next_position[1])
        logging.debug(status)
        if status is not False and status=="NONE":
            self.moveto(
                f"block:{self.block_max_tag-1}",
                (self.bottle_position[0]+self.block_image_size*self.block_x) +
                (next_position[0]*self.block_image_size),
                self.drop_position+self.block_image_size+(next_position[1]*self.block_image_size),
            )
            return True
        else:
            return False
    def landing(self):
        """
        tagのmaxtagの引き上げ
        """
        self.bottle[self.block_y][self.block_x]=self.even_block_color,self.block_max_tag
        angle_tuple:tuple=self.compass(self.angle)
        self.bottle[self.block_y+angle_tuple[1]][self.block_x+angle_tuple[0]]=self.odd_block_color,self.block_max_tag-1
        self.block_max_tag += 2
        self.drop_start()
        self.set_next_medicine(self.block_max_tag)
    def next_stage(self):
        """
        今のgameをコンプリートした際に次のステージに進む
        """
        pass                                               #工事中
    #medicine処理
    def put_block_data(self,tag_num:int,x:int,y:int,color:int):
        self.bottle[y][x] = (color,tag_num)
    def put_block(self,tag_num:int,x:int,y:int)->None:
        """
        指定された座標上にblockを移動させる
        """
        if not 0<= x <self.bottle_size[0]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        if not 0<= y <self.bottle_size[1]:
            raise DrMarioError(DrMarioError.OUT_OF_BOTTLE_RANGE)
        #なくてもいい
        #もし復活させるならcolorを引数に増やしてね！
        #self.bottle[y][x]= (color,tag_num)
        self.moveto(
            f"block:{tag_num}", 
            self.bottle_position[0]+self.block_image_size*x,
            self.bottle_position[1]+self.block_image_size*y
            )
        """
        self.create_image(self.bottle_position[0]+self.block_image_size/2+self.block_image_size*x,    
                        self.bottle_position[1]+self.block_image_size/2+self.block_image_size*y,      
                        image=image,                                                                  
                        tags=f"block:{tag_num}"                                                       
                        )
        """
    def get_block(self,x,y)->str:
        """
        指定されたbottle上の座標のブロックを返す
        範囲外の時     -> False
        何もないとき   -> "NONE"
        なんか会った時 -> それぞれの色の名前
        """
        if not 0 <= x < self.bottle_size[0]:
            return False
        if not 0 <= y < self.bottle_size[1]:
            return False
        colornum:int = self.bottle[y][x][0]
        return self.num_to_color(colornum)
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
        if e.keysym == "Left":
            self.key_left: bool = True
        if e.keysym == "Up":
            self.key_up: bool = True
        if e.keysym == "Down":
            self.key_down: bool = True
        if e.keysym == "space":
            self.__block()
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
            self.next_medicine_position[0],self.next_medicine_position[1],
            self.next_medicine_position[0]+self.next_medicine_size[0],
            self.next_medicine_position[1]+self.next_medicine_size[1],
            10
        )
        self.after_cancel(self.now_process)
        #max block tag
        self.block_max_tag:int = 0
        self.now_process = self.after(0, self.game_loop)# こっから game start
        #block init
        self.set_next_medicine(self.block_max_tag)
        self.block_max_tag += 2
        self.drop_start()
        self.set_next_medicine(self.block_max_tag)
        self.__block()

    def __block(self):
        for i in self.bottle:
            print(i)

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
        self.drop_medicine()
        self.set_keys_False() #keyをset
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
    

    #DrMario
    canvas = DrMario(frame,width=600,height=600,bg="black")
    root.bind("<Key>",canvas.key_events)
    canvas.pack()
    canvas.after(0,canvas.start_loop)
    
    root.mainloop()