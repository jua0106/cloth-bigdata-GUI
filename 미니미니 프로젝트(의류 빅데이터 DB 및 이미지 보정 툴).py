###########################의류 빅데이터 DB 구축 및 이미지 처리 툴_project2_최종혁#########
from tkinter import *
from tkinter.filedialog import *
import os.path
import math
import struct
import pymysql
from tkinter import ttk
import tempfile
import xlsxwriter
import pymysql
from tkinter.simpledialog import *
import matplotlib.pyplot as plt
import random
from PIL import Image
from PIL import ImageFilter, ImageEnhance
import tempfile
import csv
import xlrd
import xlwt
import cv2
import numpy as np
from datetime import datetime
from tkinter import ttk

IP_ADDR = 'localhost'
DB_NAME = 'fassionDB'
TBL_NAME = 'ftbl'
USER_NAME = 'root'
USER_PASS = '1234'



## 함수 선언부
#############################################################
###############<<<의류 DB 구축>>> ############################
#############################################################

## 함수 선언부
############################DB 정보 추가###########
def dataInsert():
    ##############함수선언부2#########
    def selectImageFile():
        edt3.delete(0, len(edt3.get()))
        filename = askopenfilename(parent=window, filetypes=(("이미지 파일", "*.*"), ("모든 파일", "*.*")))
        edt3.insert(0, str(filename))


    #####################################윈도우 창###########################


    window= Tk()
    window.geometry('725x810')
    window.title('DB 정보 입력')  # 제목

    # 회사명 칸
    label1=Label(window,text='회사명:')
    label1.place(x=5,y=20)
    edt1=Entry(window, width=30)  # 검색란 만들기
    edt1.place(x=55, y=20)

    #상품명 칸
    label2 = Label(window, text='상품명:')
    label2.place(x=5, y=70)
    edt2 = Entry(window, width=45)  # 검색란 만들기
    edt2.place(x=55, y=70)

    #내용
    label3 = Label(window, text='상품내용:')
    label3.place(x=5, y=130)
    edt3= Entry(window, width=20)
    edt3.place(x=499, y=123)
    button3= Button(window,text='사진선택',overrelief='solid',command=selectImageFile)
    button3.place(x=645,y=120)

    text1= Text(window)
    text1.place(x=5,y=150, width=700,height=600)

    scroll = Scrollbar(window)  # 추가
    scroll.config(command=text1.yview)  # 추가
    text1.config(yscrollcommand=scroll.set)  # 추가
    scroll.place(x=705, y=150,height=600)

    def dataSave():# 걍 함수 안에 위에 ~kan 넣어야 할듯

        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()

        try:
            fp = open(edt3.get(), 'rb')
            photodata = fp.read()
            photoInfo = edt3.get().split('/')[-1:]
            fp.close()

        except:
            photodata = 'No Image'
            photoInfo = 'No Image'
        product = edt2.get()
        company = edt1.get()  # 확장명(=파일타입)
        dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text=text1.get('1.0', END)

        sql = "INSERT INTO ftbl(id, PName, cname, savedate, ptext, photo, photoinfo) VALUES (NULL, %s, %s, %s, %s, %s, %s) "  # binary를 문자열로 변경하기 위함.
        tupleData = (product, company, dateTime,text, photodata,photoInfo)  # binary를 문자열로 변경하기 위함.
        cur.execute(sql, tupleData)  # binary를 문자열로 변경하기 위함.
        cur.close()
        con.commit()
        con.close()
        messagebox.showinfo('DB저장',' DB저장 완료!')


        ##########저장 시간#######

        status.configure(text='저장 날짜:' + dateTime)
        # window.destroy()
        # dataInsert()

    button4=Button(window,text=' DB저장 ',overrelief='solid',command=dataSave)
    button4.place(x=645,y=755)


    ## Status Bar 추가
    status = Label(window, text='저장 날짜:', bd=1, relief=SUNKEN, anchor=W)
    status.pack(side=BOTTOM, fill=X)

    window.mainloop()

###########################DB 조회########################################
def dataSearch():

    ######################윈도우창##################################
    window = Tk()
    window.geometry('525x150')
    window.title('DB 조회창')  # 제목

    # 회사명 칸
    label1 = Label(window, text='회사명:')
    label1.place(x=5, y=20)
    edt1 = Entry(window, width=30 )  # 검색란 만들기
    edt1.place(x=55, y=20)
    #####################함수안에 함수생성##############
    def companyDB():
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()
        csearch='%'+edt1.get()+'%'
        sql = "SELECT id, pName, cname , savedate FROM fTBL where cname like '"+csearch+"'"  # ID로 추출하기
        cur.execute(sql)

        rows = cur.fetchall()
        ##

        ## 새로운 윈도창 띄우기
        window2 = Toplevel(window);
        window2.title('조회목록')
        sheet = ttk.Treeview(window2, height=10);
        scroll2 = Scrollbar(window2)
        scroll2.config(command=sheet.yview)
        sheet.config(yscrollcommand=scroll2.set)
        scroll2.pack(side=RIGHT, fill=Y)
        sheet.pack()

        descs = cur.description
        colNames = [d[0] for d in descs]
        sheet.column("#0", width=80)
        sheet.heading("#0", text=colNames[0])
        sheet["columns"] = colNames[1:]
        for colName in colNames[1:]:
            sheet.column(colName, width=130)
            sheet.heading(colName, text=colName)
        for row in rows:
            sheet.insert('', 'end', text=row[0], values=row[1:])

        sheet.bind('<Double-1>', sheetDblclick2)

        cur.close()
        con.close()

    def sheetDblclick2(event):
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows, window3, window4, canvas1, paper1

        item = sheet.identify('item', event.x, event.y)  # 'I001'....
        entNum = int(item[1:], 16) - 1  ##쿼리한 결과 리스트의 순번
        id = rows[entNum][0]

        # DB에서 이미지를 다운로드
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()
        sql = "SELECT id, pName, cname ,savedate, ptext,photo,photoinfo FROM fTBL where id=" + str(id)  # ID로 이미지 추출하기
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        con.close()

        import tempfile
        # 임시 폴더
        id, pname, cname, savedate, ptext, photo, photoinfo = row
        filename = photoinfo
        fullPath = tempfile.gettempdir() + '/' + photoinfo  # 임시경로 + 파일명
        fp = open(fullPath, 'wb')  # 폴더를 지정.
        fp.write(photo)
        fp.close()

        window4 = Toplevel(window2)
        window4.title(pname)
        window4.geometry('1000x850')

        # canvas1 = Canvas(window4, height=256, width=256)
        # canvas1.create_rectangle(0, 0, 256, 256, fill='lightgray')
        # # canvas1.PhotoImage(256,256)
        # canvas1.place(x=700, y=20)

        # 회사명
        label1 = Label(window4, text='회사명:')
        label1.place(x=5, y=20)
        edt1 = Entry(window4, width=30)  # 검색란 만들기
        edt1.insert(INSERT, cname)
        edt1.place(x=55, y=20)
        # 상품명
        label2 = Label(window4, text='상품명:')
        label2.place(x=5, y=70)
        edt2 = Entry(window4, width=45)  # 검색란 만들기
        edt2.insert(INSERT, pname)
        edt2.place(x=55, y=70)
        # 상품설명
        label3 = Label(window4, text='상품설명:')
        label3.place(x=5, y=100)
        textSH = Text(window4)
        textSH.place(x=5, y=120, width=640, height=700)
        textSH.insert(INSERT, ptext)
        scroll = Scrollbar(window4, background='red', relief='solid')  # 추가
        scroll.config(command=textSH.yview)  # 추가
        textSH.config(yscrollcommand=scroll.set)  # 추가
        scroll.place(x=645, y=120, height=700)

        # 사진
        try:
            loadImageColorCV2(fullPath)
            equalImageColor7()
            label4 = Label(window4, text='<' + pname + '>', font=("고딕", 13))
            label4.place(x=830, y=292, anchor=CENTER)
        except:
            label5 = Label(window4, text='[ 사진 없음 ]', font=("고딕", 18))
            label5.place(x=830, y=128, anchor=CENTER)
            ############################
        window4.mainloop()
    button1=Button(window, text='조회',overrelief='solid',command=companyDB)
    button1.place(x=275,y=15)



    # 상품명 칸
    label2 = Label(window, text='상품명:')
    label2.place(x=5, y=70)
    edt2 = Entry(window, width=45)  # 검색란 만들기
    edt2.place(x=55, y=70)

    #####################함수안에 함수생성##############
    def productDB():
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()
        psearch='%'+edt2.get()+'%'
        sql = "SELECT id, pName, cname , savedate FROM fTBL where pname like '" + psearch + "'"  # ID로 추출하기
        cur.execute(sql)

        rows = cur.fetchall()
        ##

        ## 새로운 윈도창 띄우기
        window2 = Toplevel(window);
        window2.title('조회목록')
        sheet = ttk.Treeview(window2, height=10);
        scroll2 = Scrollbar(window2)
        scroll2.config(command=sheet.yview)
        sheet.config(yscrollcommand=scroll2.set)
        scroll2.pack(side=RIGHT, fill=Y)
        sheet.pack()

        descs = cur.description
        colNames = [d[0] for d in descs]
        sheet.column("#0", width=80)
        sheet.heading("#0", text=colNames[0])
        sheet["columns"] = colNames[1:]
        for colName in colNames[1:]:
            sheet.column(colName, width=130)
            sheet.heading(colName, text=colName)
        for row in rows:
            sheet.insert('', 'end', text=row[0], values=row[1:])

        sheet.bind('<Double-1>', sheetDblclick3)

        cur.close()
        con.close()

    def sheetDblclick3(event):
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows, window3, window4, canvas1, paper1

        item = sheet.identify('item', event.x, event.y)  # 'I001'....
        entNum = int(item[1:], 16) - 1  ##쿼리한 결과 리스트의 순번
        id = rows[entNum][0]

        # DB에서 이미지를 다운로드
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()
        sql = "SELECT id, pName, cname ,savedate, ptext,photo,photoinfo FROM fTBL where id=" + str(id)  # ID로 이미지 추출하기
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        con.close()

        import tempfile
        # 임시 폴더
        id, pname, cname, savedate, ptext, photo, photoinfo = row
        filename = photoinfo
        fullPath = tempfile.gettempdir() + '/' + photoinfo  # 임시경로 + 파일명
        fp = open(fullPath, 'wb')  # 폴더를 지정.
        fp.write(photo)
        fp.close()

        window4 =Toplevel(window2)
        window4.title(pname)
        window4.geometry('1000x850')

        # canvas1 = Canvas(window4, height=256, width=256)
        # canvas1.create_rectangle(0, 0, 256, 256, fill='lightgray')
        # # canvas1.PhotoImage(256,256)
        # canvas1.place(x=700, y=20)

        # 회사명
        label1 = Label(window4, text='회사명:')
        label1.place(x=5, y=20)
        edt1 = Entry(window4, width=30)  # 검색란 만들기
        edt1.insert(INSERT, cname)
        edt1.place(x=55, y=20)
        # 상품명
        label2 = Label(window4, text='상품명:')
        label2.place(x=5, y=70)
        edt2 = Entry(window4, width=45)  # 검색란 만들기
        edt2.insert(INSERT, pname)
        edt2.place(x=55, y=70)
        # 상품설명
        label3 = Label(window4, text='상품설명:')
        label3.place(x=5, y=100)
        textSH = Text(window4)
        textSH.place(x=5, y=120, width=640, height=700)
        textSH.insert(INSERT, ptext)
        scroll = Scrollbar(window4, background='red', relief='solid')  # 추가
        scroll.config(command=textSH.yview)  # 추가
        textSH.config(yscrollcommand=scroll.set)  # 추가
        scroll.place(x=645, y=120, height=700)
        #####
        # 사진
        try:
            loadImageColorCV2(fullPath)
            equalImageColor7()
            label4 = Label(window4, text='<' + pname + '>', font=("고딕", 13))
            label4.place(x=830, y=292, anchor=CENTER)
        except:
            label5 = Label(window4, text='[ 사진 없음 ]', font=("고딕", 18))
            label5.place(x=830, y=128, anchor=CENTER)
            ############################
        window4.mainloop()
    button2 = Button(window, text='조회',overrelief='solid',command=productDB)
    button2.place(x=380, y=67)


    ## 전체조회
    #####################함수안에 함수생성##############
    def loadDB():
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()

        sql = "SELECT id, pName, cname ,savedate FROM fTBL"  # ID로 추출하기
        cur.execute(sql)

        rows = cur.fetchall()
        ##

        ## 새로운 윈도창 띄우기
        window2 = Toplevel(window);
        window2.title('조회목록')
        sheet = ttk.Treeview(window2, height=10);
        scroll2 = Scrollbar(window2)
        scroll2.config(command=sheet.yview)
        sheet.config(yscrollcommand=scroll2.set)
        scroll2.pack(side=RIGHT, fill=Y)
        sheet.pack()

        descs = cur.description
        colNames = [d[0] for d in descs]
        sheet.column("#0", width=80)
        sheet.heading("#0", text=colNames[0])
        sheet["columns"] = colNames[1:]
        for colName in colNames[1:]:
            sheet.column(colName, width=130)
            sheet.heading(colName, text=colName)
        for row in rows:
            sheet.insert('', 'end', text=row[0], values=row[1:])

        sheet.bind('<Double-1>', sheetDblclick)

        cur.close()
        con.close()

    def sheetDblclick(event):
        global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
        global window2, sheet, rows, window3, window4, canvas1, paper1

        item = sheet.identify('item', event.x, event.y)  # 'I001'....
        entNum = int(item[1:], 16) - 1  ##쿼리한 결과 리스트의 순번
        id = rows[entNum][0]

        # DB에서 이미지를 다운로드
        con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
        cur = con.cursor()
        sql = "SELECT id, pName, cname ,savedate, ptext,photo,photoinfo FROM fTBL where id=" + str(id)  # ID로 이미지 추출하기
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        con.close()

        import tempfile
        # 임시 폴더
        id, pname, cname, savedate, ptext, photo, photoinfo = row
        filename = photoinfo
        fullPath = tempfile.gettempdir() + '/' + photoinfo  # 임시경로 + 파일명
        fp = open(fullPath, 'wb')  # 폴더를 지정.
        fp.write(photo)
        fp.close()

        # 파일 --> 메모리

        # 입력 이미지용

        ##함수내의 전역변수
        # canvas1, window4, paper1 = [None] * 3

        # UI 구성
        window4 = Toplevel(window2)
        window4.title(pname)
        window4.geometry('1000x850')


        # canvas1 = Canvas(window4, height=256, width=256)
        # canvas1.create_rectangle(0, 0, 256, 256, fill='lightgray')
        # # canvas1.PhotoImage(256,256)
        # canvas1.place(x=700, y=20)

        # 회사명
        label1 = Label(window4, text='회사명:')
        label1.place(x=5, y=20)
        edt1 = Entry(window4, width=30)  # 검색란 만들기
        edt1.insert(INSERT, cname)
        edt1.place(x=55, y=20)
        # 상품명
        label2 = Label(window4, text='상품명:')
        label2.place(x=5, y=70)
        edt2 = Entry(window4, width=45)  # 검색란 만들기
        edt2.insert(INSERT, pname)
        edt2.place(x=55, y=70)
        # 상품설명
        label3 = Label(window4, text='상품설명:')
        label3.place(x=5, y=100)
        textSH = Text(window4)
        textSH.place(x=5, y=120, width=640, height=700)
        textSH.insert(INSERT, ptext)
        scroll = Scrollbar(window4, background='red', relief='solid')  # 추가
        scroll.config(command=textSH.yview)  # 추가
        textSH.config(yscrollcommand=scroll.set)  # 추가
        scroll.place(x=645, y=120, height=700)
        # 사진
        try:
            loadImageColorCV2(fullPath)
            equalImageColor7()
            label4 = Label(window4, text='<' + pname + '>', font=("고딕", 13))
            label4.place(x=830, y=292, anchor=CENTER)
        except:
            label5 = Label(window4, text='[ 사진 없음 ]', font=("고딕", 18))
            label5.place(x=830, y=128, anchor=CENTER)
            ############################
        window4.mainloop()

    button3 = Button(window, text='전체조회', overrelief='solid',command=loadDB)
    button3.place(x=240, y=110)





#############################################################
############### <<<이미지 처리>>> #############################
#############################################################



###################필요한 함수 생성###################
def displayImageColor7() : #고정된 이미지
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename,window4,canvas1,paper1

    if canvas != None:
        canvas.destroy()
    ### 고정된 화면을 준비 ###
    VIEW_X, VIEW_Y = 256, 256
    if VIEW_X >= outW and VIEW_Y >= outH:  # 원영상이 512이하면
        VIEW_X = outW;
        VIEW_Y = outH
        step = 1
    else:
        if outW > outH:
            step = outW / VIEW_X
        else:
            step = outH / VIEW_X
    #window.geometry(str(int(VIEW_X * 1.2)) + 'x' + str(int(VIEW_Y * 1.2)))  # 여백칸 1.2 의 값을 수정하여 고침
    # canvas1 = Canvas(window4, height=VIEW_Y, width=VIEW_X)
    # paper1 = PhotoImage(height=VIEW_Y, width=VIEW_X)
    # canvas1.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper1, state='normal')

    canvas1 = Canvas(window4, height=VIEW_Y, width=VIEW_X)
    # canvas = Canvas(canvas1,height=int(VIEW_Y * 0.8), width=int(VIEW_X * 0.8))
    # canvas1 = Canvas(window4, height=VIEW_Y, width=VIEW_X)
    canvas1.create_rectangle(0, 0, 256, 256, fill='lightgray')
    paper1 = PhotoImage(height=int(VIEW_Y * 0.9), width=int(VIEW_X * 0.9))
    canvas1.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper1, state='normal', anchor=CENTER)
    import numpy
    rgbString = ''  # 여기에 전체 픽셀 문자열을 저장할 계획
    for i in numpy.arange(0, outH, step):
        tmpString = ''
        for k in numpy.arange(0, outW, step):
            i = int(i);
            k = int(k)
            try:
                r, g, b = outImageR[i][k], outImageG[i][k], outImageB[i][k]
            except:
                pass
            tmpString += ' #%02x%02x%02x' % (r, g, b)
        rgbString += '{' + tmpString + '} '
    paper1.put(rgbString)
    canvas1.place(x=700, y=20)

def displayImageColor() : #고정된 이미지
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    if canvas != None:
        canvas.destroy()
    ### 고정된 화면을 준비 ###
    VIEW_X, VIEW_Y = 512, 512
    if VIEW_X >= outW and VIEW_Y >= outH:  # 원영상이 512이하면
        VIEW_X = outW;
        VIEW_Y = outH
        step = 1
    else:
        if outW > outH:
            step = outW / VIEW_X
        else:
            step = outH / VIEW_X
    window.geometry(str(int(VIEW_X * 1.2)) + 'x' + str(int(VIEW_Y * 1.2)))  # 여백칸 1.2 의 값을 수정하여 고침
    canvas = Canvas(window, height=VIEW_Y, width=VIEW_X)
    paper = PhotoImage(height=VIEW_Y, width=VIEW_X)
    canvas.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper, state='normal')
    import numpy
    rgbString = ''  # 여기에 전체 픽셀 문자열을 저장할 계획
    for i in numpy.arange(0, outH, step):
        tmpString = ''
        for k in numpy.arange(0, outW, step):
            i = int(i);
            k = int(k)
            try:
                r, g, b = outImageR[i][k], outImageG[i][k], outImageB[i][k]
            except:
                pass
            tmpString += ' #%02x%02x%02x' % (r, g, b)
        rgbString += '{' + tmpString + '} '
    paper.put(rgbString)
    canvas.pack(expand=1, anchor=CENTER)
    status.configure(text='이미지 정보:' + str(outW) + 'x' + str(outH))


def displayImageColor1() : #고정 안된 디스플레이
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    if canvas != None :
        canvas.destroy()
    window.geometry(str(outW) + 'x' + str(outH))
    canvas = Canvas(window, height=outH, width=outW)
    paper = PhotoImage(height=outH, width=outW)
    canvas.create_image((outW / 2, outH / 2), image=paper, state='normal')

    rgbString = '' # 여기에 전체 픽셀 문자열을 저장할 계획
    step = 1
    for i in range(0, outH, step) :
        tmpString = ''
        for k in range(0, outW, step) :
            r,g,b = outImageR[i][k],outImageG[i][k],outImageB[i][k]
            tmpString += ' #%02x%02x%02x' % (r, g, b)
        rgbString += '{' + tmpString + '} '
    paper.put(rgbString)
    canvas.pack()
    status.configure(text='이미지 정보:' + str(outW) + 'X' + str(outH))

def equalImageColor7():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    global window4, canvas1, paper1
    outImageR,outImageG,outImageB =[],[],[]  # 초기화
    # outImage의 크기를 결정
    outH = inH;  outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH) :
        for k in range(inW) :
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
    ################################
    displayImageColor7()

def equalImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    outImageR,outImageG,outImageB =[],[],[]  # 초기화
    # outImage의 크기를 결정
    outH = inH;  outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH) :
        for k in range(inW) :
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
    ################################
    displayImageColor()



###########################이미지 열기#######################
def loadImageColorCV2(fname) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR,outImageG,outImageB, filename, photo, cvPhoto
    inImageR,inImageG,inImageB = [],[],[] # 초기화

    ###############################################
    ## openCV용으로 읽어서 보관 + Pillow용으로 변환
    cvData= cv2.imread(fname)
    cvPhoto = cv2.cvtColor(cvData, cv2.COLOR_BGR2RGB) #얘는 원래 BGR인데 우리 코드가 RGB로 되어있으므로 변환해줌
    photo= Image.fromarray(cvPhoto)
    ##############################################################
    # 파일 크기 계산
    photo = Image.open(fname)
    inH= photo.height; inW= photo.width
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageR.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageG.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageB.append(tmp)
    # 파일 --> 메모리로 한개씩 옮기기
    photoRGB = photo.convert('RGB')

    for  i  in  range(inH) :
        for k in range(inW) :
            r,g,b = photoRGB.getpixel((k,i)) # 1개 픽셀값을 읽음 (0~255)
            inImageR[i][k] = r; inImageG[i][k] = g; inImageB[i][k] = b
    ##print(inImageR[100][100],inImageG[100][100],inImageB[100][100])

def openOpenCV() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    filename = askopenfilename(parent=window, filetypes=(("영상 파일", "*.jpg;*.png;*.bmp;*.tif;*.jpeg"), ("모든 파일", "*.*")))
    if filename == "" or filename == None :
        return

    if filename.split('.')[1].upper()!='JPG'and filename.split('.')[1].upper()!='PNG'and \
        filename.split('.')[1].upper()!='JPEG' and filename.split('.')[1].upper()!='bmp' \
            and filename.split('.')[1].upper()!='tif':
        messagebox.showinfo('오류!','.jp(e)g, .png, .bmp, .tif 만 작업가능합니다.')
        return
    # 파일 --> 메모리
    loadImageColorCV2(filename)

    # Input --> outPut으로 동일하게 만들기.
    equalImageColor()

def toColorImage(photo2, scale=1) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = int(inH*scale);  outW = int(inW*scale)
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 영상 처리 알고리즘을 구현 ####
    photoRGB = photo2.convert('RGB')
    for i in range(outH):
        for k in range(outW):
            r, g, b = photoRGB.getpixel((k, i))  #
            outImageR[i][k] = r;
            outImageG[i][k] = g;
            outImageB[i][k] = b
    ################################
    displayImageColor()

###########################이미지 저장#######################
######################예비저장#
def saveImageFile():
    global window, canvas, paper, inW, inH, outW, outH
    global inImageR, inImageG, inImageB, outImageR, outImageG
    global outImageB, filename, cvPhoto
    outImage = []
    #saveroo = asksaveasfilename(title='export filename', initialdir='/', defaultextension='jpg',
    #                                 filetypes=(("이미지 파일", "*.jpg;*.png;*.bmp;*.tif"), ("모든 파일", "*.*")))
    saveFp = asksaveasfile(parent=window, mode="wb", defaultextension=".jpg",
                           filetypes=(("JPG 파일", "*.jpg"), ("모든 파일", "*.*")))

    outImage = np.zeros((outH,outW,3), dtype = np.uint8)

    for i in range(outH):
        for k in range(outW):
            outImage[i ][k] = outImageB[i][k], outImageG[i][k], outImageR[i][k]
    outImage = np.array(outImage)
    cv2.imwrite(saveFp.name,outImage)
##########################################################################
def saveImageColor() :# 교수님이 올리신 컬러이미지 저장 함수
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    outArray = []
    for i in range(outH) :
        tmpList = []
        for k in range(outW) :
            tup = tuple([outImageR[i][k], outImageG[i][k], outImageB[i][k]])
            tmpList.append(tup)
        outArray.append(tmpList)

    outArray = np.array(outArray)
    savePhoto = Image.fromarray(outArray.astype('uint8'), 'RGB')

    saveFp = asksaveasfile(parent=window, mode='w', defaultextension=".", filetypes=(
        ("그림파일", "*.png;*.jpg;*.bmp;*.tif"),  ("모든파일", "*.*")))

    savePhoto.save(saveFp.name)

    print('OK! save')

###########################밝게하기#######################
def addImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    outImageR,outImageG,outImageB =[],[],[]  # 초기화
    # outImage의 크기를 결정
    outH = inH;  outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    value = askinteger("밝게할 값", "값 입력")
    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH) :
        for k in range(inW) :
            if inImageR[i][k] + value > 255 :
                outImageR[i][k] = 255
            else :
                outImageR[i][k] = inImageR[i][k] + value
            if inImageG[i][k] + value > 255:
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = inImageG[i][k] + value
            if inImageB[i][k] + value > 255 :
                outImageB[i][k] = 255
            else :
                outImageB[i][k] = inImageB[i][k] + value
    ################################
    displayImageColor()

###########################어둡게 하기#######################
def darkImageColor(): #어둡게하는 이미지
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH
    outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    value= askinteger('어둡게할 값','값 입력')
    #####영상 처리 알고리즘을 구현 #####
    for i in range(inH):
        for k in range(inW):
            if inImageR[i][k] - value <0: #픽셀 값이 기준이 됨
                outImageR[i][k]=0
            else:
                outImageR[i][k] = inImageR[i][k]-value
            if inImageG[i][k] - value <0: #픽셀 값이 기준이 됨
                outImageG[i][k]=0
            else:
                outImageG[i][k] = inImageG[i][k]-value
            if inImageB[i][k] - value <0: #픽셀 값이 기준이 됨
                outImageB[i][k]=0
            else:
                outImageB[i][k] = inImageB[i][k]-value
    ############################
    displayImageColor()

#######################미러링 상하#####################################
def mirror1CV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    #### CV2 메소드로 구현하기 --> photo2로 넘기기####
    cvPhoto2 = cvPhoto[:]  # cvPhoto를 카피(복사)한 것이랑 같음
    cvPhoto2 = cv2.flip(cvPhoto2, 0)
    photo2 = Image.fromarray(cvPhoto2)

    ################################
    toColorImage(photo2)

#######################미러링 좌우#####################################
def mirror2CV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    #### CV2 메소드로 구현하기 --> photo2로 넘기기####
    cvPhoto2 = cvPhoto[:]  # cvPhoto를 카피(복사)한 것이랑 같음
    cvPhoto2 = cv2.flip(cvPhoto2, 1)
    photo2 = Image.fromarray(cvPhoto2)

    ################################
    toColorImage(photo2)

######################openCV 확대/축소########################
def scaleCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    ####CV2 메소드로 구현하기 --> photo2로 넘기기####
    scale =askfloat('스케일 개수','확대/축소 값--->', minvalue=0.1, maxvalue=10.0) #실수값이 있으므로 askfloatd을 쓴다.

    cvPhoto2 = cvPhoto[:]  # cvPhoto를 카피(복사)한 것이랑 같음
    cvPhoto2 = cv2.resize(cvPhoto2, None, fx=scale, fy=scale)
    photo2 = Image.fromarray(cvPhoto2)
    ####################################################
    toColorImage(photo2,scale)

####################회전#############
def rotateCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    ####CV2 메소드로 구현하기 --> photo2로 넘기기####
    angle =askinteger('각도','회전각--->')

    cvPhoto2 = cvPhoto[:]  # cvPhoto를 카피(복사)한 것이랑 같음
    rotate_matrix=cv2.getRotationMatrix2D((inW//2,inH//2),angle, 1)#cv2.getRotationMatrix2D (기준점, 각도, 스케일)
    cvPhoto2 = cv2.warpAffine(cvPhoto2,rotate_matrix,(inW,inH))
    photo2 = Image.fromarray(cvPhoto2)
    ####################################################
    toColorImage(photo2)
#################################################

################################################################################################

####################흑백변환#############
def bwImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    outImageR, outImageG, outImageB = [], [], []
    # outImage의 크기를 결정
    outH = inH;  outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 평균값 구하기 ###
    hap = 0
    hap2=0
    hap3=0
    for i in range(inH) :
        for k in range(inW) :
            hap += inImageR[i][k]
            hap2 += inImageG[i][k]
            hap3 += inImageB[i][k]
    avg1 = hap // (inH * inW)
    avg2 = hap2 // (inH * inW)
    avg3 = hap3 // (inH * inW)

    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH) :
        for k in range(inW) :
            if inImageR[i][k] >= avg1 and inImageG[i][k] >= avg2 and inImageB[i][k] >= avg3:
                outImageR[i][k] = 255
                outImageG[i][k] = 255
                outImageB[i][k] = 255
            else :
                outImageR[i][k] = 0
                outImageG[i][k] = 0
                outImageB[i][k] = 0
    ################################
    displayImageColor()

#########반전하기#############
def reverseImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH
    outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH) :
        for k in range(inW) :
            outImageR[i][k] = 255 - inImageR[i][k]
            outImageG[i][k] = 255 - inImageG[i][k]
            outImageB[i][k] = 255 - inImageB[i][k]
    ################################
    displayImageColor()


####################그레이 스케일#############
def greyScaleCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto


    #### CV2 메소드로 구현하기 --> photo2로 넘기기####
    cvPhoto2 = cvPhoto[:] #cvPhoto를 카피(복사)한 것이랑 같음
    cvPhoto2 =cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)
    photo2 = Image.fromarray(cvPhoto2)

    ################################
    toColorImage(photo2)

####################블러링#############

def blurCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    ####블러링을 CV2 메소드로 구현하기 --> photo2로 넘기기####

    cvPhoto2 = cvPhoto[:]  # cvPhoto를 카피(복사)한 것이랑 같음
    maskoption=askinteger('마스크', '마스크인자--->')
    mask = np.ones((maskoption, maskoption), np.float32) / (maskoption*maskoption)  # 마스크 행렬 만듬 #나눠야하므로 여기서는 엠보싱과 다르게 1로 채움
    cvPhoto2 = cv2.filter2D(cvPhoto2, -1, mask)
    photo2 = Image.fromarray(cvPhoto2)

    ################################
    toColorImage(photo2)

#######################샤프닝################
def sharpningColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot

    ## pillow  라이브러리가 제공해주는 메소드(함수)를 사용해서 처리하자
    photo2 = photo.copy()
    photo2 = photo2.filter(ImageFilter.SHARPEN)

    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH;
    outW = inW

    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)

    #### 영상 처리 알고리즘을 구현 ####
    photoRGB = photo2.convert('RGB')
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))  # 한 픽셀 단위로 값을 가져옴/
            outImageR[i][k] = r
            outImageG[i][k] = g
            outImageB[i][k] = b

    ################################
    displayImageColor()

#######################스무싱################
def smoothingColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot

    ## pillow  라이브러리가 제공해주는 메소드(함수)를 사용해서 처리하자
    photo2 = photo.copy()
    photo2 = photo2.filter(ImageFilter.SMOOTH)

    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH;
    outW = inW

    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)

    #### 영상 처리 알고리즘을 구현 ####
    photoRGB = photo2.convert('RGB')
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))  # 한 픽셀 단위로 값을 가져옴/
            outImageR[i][k] = r
            outImageG[i][k] = g
            outImageB[i][k] = b

    ################################
    displayImageColor()

#############################에지검출##########################
def edgingColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot
    ## pillow  라이브러리가 제공해주는 메소드(함수)를 사용해서 처리하자
    photo2 = photo.copy()
    photo2 = photo2.filter(ImageFilter.EDGE_ENHANCE)

    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH;
    outW = inW

    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)

    #### 영상 처리 알고리즘을 구현 ####
    photoRGB = photo2.convert('RGB')
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))  # 한 픽셀 단위로 값을 가져옴/
            outImageR[i][k] = r
            outImageG[i][k] = g
            outImageB[i][k] = b

    ################################
    displayImageColor()

#########################카툰화################
def cartoonCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto ,saveroot


    ####CV2 메소드로 구현하기 --> photo2로 넘기기####
    cvPhoto2 = cvPhoto[:] #cvPhoto를 카피(복사)한 것이랑 같음
    cvPhoto2 =cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)
    cvPhoto2 =cv2.medianBlur(cvPhoto2,7)

    edges= cv2.Laplacian(cvPhoto2,cv2.CV_8U,ksize=5)
    ret, mask= cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY_INV)
    cvPhoto2 = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    photo2 = Image.fromarray(cvPhoto2)
    ####################################################
    toColorImage(photo2)

####################엠보싱#############
def embossingCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto


    ####엠보싱을 CV2 메소드로 구현하기 --> photo2로 넘기기####
    cvPhoto2 = cvPhoto[:] #cvPhoto를 카피(복사)한 것이랑 같음
    mask= np.zeros((3,3), np.float32) #마스크 행렬 만듬
    mask[0][0]= -1 ; mask[2][2]=1
    cvPhoto2 = cv2.filter2D(cvPhoto2,-1,mask)
    cvPhoto2 +=127 #이 구문을 실행 안하면 검은 엠보싱 됨.
    photo2 = Image.fromarray(cvPhoto2)

    ################################
    toColorImage(photo2)

####################컨투어#############
def contouringColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, saveroot

    ## pillow  라이브러리가 제공해주는 메소드(함수)를 사용해서 처리하자
    photo2 = photo.copy()
    photo2 = photo2.filter(ImageFilter.CONTOUR)

    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH;
    outW = inW

    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)

    #### 영상 처리 알고리즘을 구현 ####
    photoRGB = photo2.convert('RGB')
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))  # 한 픽셀 단위로 값을 가져옴/
            outImageR[i][k] = r
            outImageG[i][k] = g
            outImageB[i][k] = b

    ################################
    displayImageColor()

################################################################################



########전역변수########
window, canvas, paper = [None] * 3;  inW, inH, outW, outH = [200] * 4
inImage, outImage = [], []
filename =None
inImageR, inImageG, inImageB, outImageR, outImageG,outImageB = [],[],[],[],[],[]
photo, cvPhoto= None, None #pillow용, openCV용
saveroot=None
con, cur = [None] * 2  # 연결자, 커서
sql = ""  # 쿼리문자열
row = None





######## 메인 코드부############
window = Tk(); window.title('의류 빅데이터 DB / 이미지 보정 툴 (Ver.2019)')
window.geometry('500x300')

## Status Bar 추가
status =Label(window, text='이미지정보:', bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM,fill=X) #맨밑에 이미지 정보라고 나옴

## 메뉴 추가하기
mainMenu = Menu(window) # 메뉴 전체 껍질
window.config(menu=mainMenu)


############################의류 DB 메뉴#########################
clothDB= Menu(window)
mainMenu.add_cascade(label='의류 DB',menu=clothDB)
#
dbProcess = Menu(clothDB)
clothDB.add_cascade(label="DB", menu=dbProcess)
dbProcess.add_command(label="DB 정보 입력", command=dataInsert)
dbProcess.add_command(label="DB 조회", command=dataSearch)



############################이미지 처리 메뉴##############################
ImageMenu= Menu(window)
mainMenu.add_cascade(label='이미지 처리',menu=ImageMenu)
#
ImagefileMenu = Menu(ImageMenu)
ImageMenu.add_cascade(label="이미지 파일", menu=ImagefileMenu)
ImagefileMenu.add_command(label="이미지 열기", command=openOpenCV) #opencv
ImagefileMenu.add_command(label="이미지 저장", command=saveImageFile) #raw 저장에서 수정해야 할듯 for문이 관건임
#
ImageBaseMenu = Menu(ImageMenu)
ImageMenu.add_cascade(label="기본효과", menu=ImageBaseMenu)
ImageBaseMenu.add_command(label="밝게하기", command=addImageColor) #칼라
ImageBaseMenu.add_command(label='어둡게하기',command=darkImageColor) #칼라
ImageBaseMenu.add_command(label="미러링(상하)", command=mirror1CV2)#opencv
ImageBaseMenu.add_command(label="미러링(좌우)", command=mirror2CV2)#opencv
ImageBaseMenu.add_command(label="확대/축소", command=scaleCV2)#opencv
ImageBaseMenu.add_command(label="회전", command=rotateCV2) #opencv
#
ImageSpecialMenu = Menu(ImageMenu)
ImageMenu.add_cascade(label="특수효과", menu=ImageSpecialMenu)

ImageSpecialMenu.add_command(label="흑백", command=bwImageColor) #칼라
ImageSpecialMenu.add_command(label="반전하기", command=reverseImageColor) #칼라
ImageSpecialMenu.add_command(label="그레이스케일", command=greyScaleCV2)#opencv
ImageSpecialMenu.add_separator()
ImageSpecialMenu.add_command(label="블러링", command=blurCV2) #정도 주기 #opencv
ImageSpecialMenu.add_command(label="샤프닝", command=sharpningColor) #칼라
ImageSpecialMenu.add_command(label="스무싱", command=smoothingColor) #칼라
ImageSpecialMenu.add_command(label="엣지칼라", command=edgingColor) #칼라
ImageSpecialMenu.add_separator()
ImageSpecialMenu.add_command(label="카툰화", command=cartoonCV2)#opencv
ImageSpecialMenu.add_command(label="엠보싱칼라", command=embossingCV2)#opencv
ImageSpecialMenu.add_command(label="컨투어칼라", command=contouringColor)#칼라

ImageMenu.add_separator()
ImageMenu.add_command(label="이미지 원래대로", command=equalImageColor) #equiimage

##########################
window.mainloop()