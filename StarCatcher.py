#Part of motionDetection is cited from:
#http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
#CornerDetection is cited from:
#https://www.youtube.com/watch?v=IXyO2O-I2bs
#rgbString readFiles and writeFiles from 15-112 website notes
#run function cited from barebones setup from 15112 website notes

from tkinter import *
import numpy as np
import cv2
import random
from PIL import Image, ImageTk
import math
import copy

####################################
# customize these functions
####################################

def init(data):
    data.mode="instruction"
    
    instructionInit(data)
    #playInit(data)

def mousePressed(event, data):
    if (data.mode == "instruction"):  instructionMousePressed(event, data)
    elif (data.mode=="calibrate"):    calibrateMousePressed(event, data)
    elif (data.mode == "play"):       playMousePressed(event, data)
    elif (data.mode == "help"):       helpMousePressed(event, data)
    elif (data.mode == "over"):       overMousePressed(event, data)

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    if (data.mode == "instruction"):  instructionScreenTimerFired(data)
    elif (data.mode=="calibrate"):    calibrateimerFired(data)
    elif (data.mode == "play"):       playTimerFired(data)
    elif (data.mode == "help"):       helpTimerFired(data)
    elif (data.mode == "over"):       overTimerFired(data)
    
def redrawAll(canvas, data):
    if (data.mode == "instruction"):  instructionRedrawAll(canvas, data)
    elif (data.mode=="calibrate"):    calibrateRedrawAll(canvas, data)
    elif (data.mode == "play"):       playRedrawAll(canvas, data)
    elif (data.mode == "help"):       helpRedrawAll(canvas, data)
    elif (data.mode == "over"):       overRedrawAll(canvas, data)
    
###instruction mode
def instructionInit(data):
    data.bttnW=75
    data.bttnH=30
    data.intro=[
               "Hello! You're gonna help me to collect STARS",
               "Place bars on board to make me bounce within window",
               "Please don't let me collapse with bomb!",
               "I can help you shoot the bomb,",
               "but you have to make me in right position.",
               "Once I shoot a bomb, you will get two extra stars on board,",
               "and 5 stars will be added to your collection",
               "Purple star will protect you from the bomb once,",
               "so is the largest star.",
               "Please adjust your camera ans board,",
               "to make the board fit in your window.",
               "click 'START' to start calibrition"
               ]

def instructionMousePressed(event, data):
    if (event.x<data.width/2+data.bttnW and 
        event.x>data.width/2-data.bttnW and
        event.y<5*data.height/6+data.bttnH and 
        event.y>5*data.height/6-data.bttnH):
            data.mode='calibrate'
            calibrateInit(data)

def instructionScreenTimerFired(data):
    pass

def instructionRedrawAll(canvas, data):
    margin=5
    x0,x1=data.width/2-data.bttnW,data.width/2+data.bttnW
    y0,y1=5*data.height/6-data.bttnH,5*data.height/6+data.bttnH
    #draw button
    canvas.create_rectangle(0,0,data.width,data.height,fill='gray85',width=0)
    canvas.create_rectangle(x0,y0,x1,y1,fill='gray70',width=0)
    canvas.create_rectangle(x0+margin,y0+margin,x1-margin,y1-margin,
                            outline='white',width=1)
    canvas.create_text(data.width/2,5*data.height/6,text='START',
                       fill='white',font='Helvetica 20 bold')
    #draw instruction
    for i in range(len(data.intro)):
        canvas.create_text(data.width/2,data.height/7+25*i,text=data.intro[i],
                           fill='gray60',font='Helvetica 10')

###calibration mode
def calibrateInit(data):
    data.finishBttnW=75
    data.finishBttnH=30
    data.imgtk=None

def calibrateMousePressed(event, data):
    #if pressed play
    if (event.x<data.width/2+data.finishBttnW and 
        event.x>data.width/2-data.finishBttnW and
        event.y<3*data.height/4+data.finishBttnH and 
        event.y>3*data.height/4-data.finishBttnH):
            data.mode='play'
            playInit(data)

#Part of motionDetection is cited from:
#http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
def calibrateimerFired(data):
    #Get data.frame from camera
    _, data.frame = data.cap.read()
    #Transfer the data.frame into tkinter data.frame format.
    #data.frame = cv2.flip(data.frame, 1)
    cv2image = cv2.cvtColor(data.frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    data.imgtk = ImageTk.PhotoImage(image=img)

def calibrateRedrawAll(canvas, data):
    canvas.create_image(0, 0, anchor=NW, image=data.imgtk)
    margin=5
    x0,x1=data.width/2-data.finishBttnW,data.width/2+data.finishBttnW
    y0,y1=3*data.height/4-data.finishBttnH,3*data.height/4+data.finishBttnH
    #draw button
    canvas.create_rectangle(x0,y0,x1,y1,fill='gray70',width=0)
    canvas.create_rectangle(x0+margin,y0+margin,x1-margin,y1-margin,
                            outline='white',width=1)
    canvas.create_text(data.width/2,3*data.height/4,text='PLAY',
                       fill='white',font='Helvetica 20 bold')
    
###play mode
def playInit(data):
    data.frame=None
    #start corner detection
    data.startCD=False
    data.level=1
    data.stars=[]
    data.bombs=[]
    data.explodeLoc=[]
    data.moveStars=[]
    data.superMode=False
    data.pause=False
    data.playerName=''
    data.showRecords=False
    
    jumpInit(data)
    detectionDataInit(data)
    uiInit(data)
    charInit(data)
    starInit(data)
    bombInit(data)

def jumpInit(data):
    data.lineVect=None
    data.lineStart=None
    data.lineEnd=None

def detectionDataInit(data):
    data.imgtk=None
    data.corners=None
    data.t_minus = cv2.cvtColor(data.cap.read()[1], cv2.COLOR_RGB2GRAY)
    data.t = cv2.cvtColor(data.cap.read()[1], cv2.COLOR_RGB2GRAY)
    data.t_plus = cv2.cvtColor(data.cap.read()[1], cv2.COLOR_RGB2GRAY)

def uiInit(data):
    data.topLeftY=30
    
    data.pauseKeyX=10*data.width/12
    data.pauseKeyW=15
    data.pauseKeyH=15
    
    data.helpKeyX=11*data.width/12
    data.helpKeyW=30
    data.helpKeyH=15
    
    data.starNum=0
    data.starNumX=data.pauseKeyX-1.5*data.pauseKeyW
    data.starX=data.pauseKeyX-3*data.pauseKeyW

def charInit(data):
    data.char=Ninja(20,20)
    data.symbolStar=Star(data.starX,data.topLeftY)

def starInit(data):
    #generate stars
    for i in range (data.level):
        x,y,color,angle,radi=generateStar(data)
        x=random.randint(data.width//5,4*data.width//5)
        y=random.randint(data.height//5,4*data.height//5)
        color=random.randint(0,4)
        if color==0:
            r,g,b=254,225,97
        elif color==1:
            r,g,b=244,123,94
        elif color==2:
            r,g,b=254,174,147
        elif color==3:
            r,g,b=254,118,120
        else:
            r,g,b=186,142,177
        color=rgbString(r,g,b)
        angle=random.randint(0,60)
        radi=random.randint(12,24)
        data.stars.append(Star(x,y,color,angle,radi))

def generateStar(data):
    #random position, random size and random color
    x=random.randint(data.width//5,4*data.width//5)
    y=random.randint(data.height//5,4*data.height//5)
    color=random.randint(0,4)
    if color==0:
        r,g,b=254,225,97
    elif color==1:
        r,g,b=244,123,94
    elif color==2:
        r,g,b=254,174,147
    elif color==3:
        r,g,b=254,118,120
    else:
        r,g,b=186,142,177
    color=rgbString(r,g,b)
    angle=random.randint(0,60)
    radi=random.randint(12,24)
    return x,y,color,angle,radi

def bombInit(data):
    for i in range (data.level//2):
        x=random.randint(data.width//5,4*data.width//5)
        y=random.randint(data.height//5,4*data.height//5)
        data.bombs.append(Bomb(x,y))

def playMousePressed(event, data):
    #check if pressed help or pause
    (pX0,pY0,pX1,pY1)=buttonBound(data.pauseKeyX,
                                  data.topLeftY,
                                  data.pauseKeyW,
                                  data.pauseKeyH)
    (hX0,hY0,hX1,hY1)=buttonBound(data.helpKeyX,
                                  data.topLeftY,
                                  data.helpKeyW,
                                  data.helpKeyH)
    if event.x>=pX0 and event.x<=pX1 and event.y>=pY0 and event.y<=pY1:
        data.pause=not data.pause
    elif event.x>=hX0 and event.x<=hX1 and event.y>=hY0 and event.y<=hY1:
        data.pause=True
        data.mode='help'

def playTimerFired(data):
    
    #Get data.frame from camera
    _, data.frame = data.cap.read()
    #Transfer the data.frame into tkinter data.frame format.
    #data.frame = cv2.flip(data.frame, 1)
    cv2image = cv2.cvtColor(data.frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    data.imgtk = ImageTk.PhotoImage(image=img)
    
    if data.pause==False:
    
        data.char.fall()
        
        if (data.char.center[0]<1.2*data.char.radi or 
            data.char.center[0]>data.width-1.5*data.char.radi):
                data.char.dir[0]*=-1
        if (data.char.center[1]<1.2*data.char.radi or 
            data.char.center[1]>data.height-1.5*data.char.radi):
                data.char.dir[1]*=-1
        
        #check is char collapse with a bomb or out of board
        # if bombExplode(data) and not outCanvas(data,data.char.center):
        if bombExplode(data):
            if data.superMode==True:
                data.superMode==False
                data.char.color='gray50'
            elif data.char.radi>20:
                data.char.radi=20
            else:
                data.mode='over'
                overInit(data)
        # elif outCanvas(data,data.char.center):
        #     data.mode='over'
        #     overInit(data)
        
        if not objectMoving(data) and data.corners==None and data.startCD==True:
            data.corners=cornerDetection(data)
            #get barrier and swith dir
            (data.lineStart,data.lineEnd)=getLine(data)
            data.lineVect=(data.lineStart[0]-data.lineEnd[0],
                        data.lineStart[1]-data.lineEnd[1])
        elif objectMoving(data):
            data.corners=None
            data.lineVect=None
            if data.startCD==False:
                data.startCD=True
        
        #if char hit the line, shift the moving direction
        if data.lineVect!=None and hitTheLine(data):
            data.char.dir=getNewDir(data)
            # print('new Dir',data.char.dir)
        
        #check if char eat a star
        if eatStar(data)!=None:
            data.starNum+=1
            starIndex=eatStar(data)
            if data.stars[starIndex].radi==24:
                data.char.radi*=1.5
            if data.stars[starIndex].color=='#ba8eb1':
                data.superMode=True
                data.char.color='#ba8eb1'
            data.stars.pop(starIndex)
            if data.stars==[] and data.bombs==[]:
                data.level+=1
                starInit(data)
                bombInit(data)
        
        #check if we should shoot
        if data.bombs!=[] and data.char.bullets==None:
            for bomb in data.bombs:
                if abs(bomb.y-data.char.center[1])<bomb.radi:
                    xDist=bomb.x-data.char.center[0]
                    data.char.shootDir=xDist//abs(xDist)
                    data.char.bullets=copy.copy(data.char.center)
                    break
        elif data.bombs!=[] and data.char.bullets!=None:
            data.char.shoot()
            if data.char.bullets[0]<=0 or data.char.bullets[0]>=data.width:
                data.char.bullets=None
            
        #check if shooted
        if data.char.bullets!=None:
            for i in range (len(data.bombs)):
                bomb=data.bombs[i]
                if shooted(data,bomb.x,bomb.y,bomb.radi):
                    print('***shooted***')
                    data.explodeLoc.append(Explosion(bomb.x,bomb.y,1))
                    
                    addStars=[]
                    for j in range (2):
                        x,y,color,angle,radi=generateStar(data)
                        addStars.append(BonusStar(bomb.x,bomb.y,
                                                  color,angle,radi))
                    data.moveStars.append(addStars)
                    
                    data.bombs.pop(i)
                    data.char.bullets=None
                    data.starNum+=5
                break
        
        #if shooted draw explosion
        if data.explodeLoc!=[]:
            for i in range (len(data.explodeLoc)):
                explosion=data.explodeLoc[i]
                if explosion.depth==10:
                    data.explodeLoc.pop(i)
                    data.stars+=data.moveStars.pop(i)
                    break
                else:
                    explosion.explode()
                    for star in data.moveStars[i]:
                        star.move(data.width/5,4*data.width/5,
                                data.height/5,4*data.height/5)

def shooted(data,x,y,dist):
    distX=data.char.bullets[0]-x
    distY=data.char.bullets[1]-y
    return math.hypot(distX,distY)<=2*dist

def outCanvas(data,Pt):
    return (Pt[0]<0 or Pt[0]>data.width or Pt[1]<0 or Pt[1]>data.height)

def bombExplode(data):
    #if dist small enough bomb explode
    for bomb in data.bombs:
        distX=bomb.x-data.char.center[0]
        distY=bomb.y-data.char.center[1]
        return math.hypot(distX,distY)<=data.char.radi+22.5

def eatStar(data):
    for i in range (len(data.stars)):
        star=data.stars[i]
        distX=star.x-data.char.center[0]
        distY=star.y-data.char.center[1]
        if math.hypot(distX,distY)<=star.lightRadi+data.char.radi:
            return i
    
def getLine(data):
    #get the line from the detected corners
    xList=[]
    yList=[]
    for corner in data.corners:
        xList.append(corner[0])
        yList.append(corner[1])
    xMax=max(xList)
    xMin=min(xList)
    if xMax!=xMin:
        yMax=yList[xList.index(xMax)]
        yMin=yList[xList.index(xMin)]
    else:
        yMax=max(yList)
        yMin=min(yList)
    return ((xMax,yMax),(xMin,yMin))

def getNewDir(data):
    #formula from 21-241 linear algebra notes
    x=data.char.dir[0]
    y=data.char.dir[1]
    a=data.lineVect[0]
    b=data.lineVect[1]
    #projection of curDir on line
    p1=(a*(a*x+b*y)/(a**2+b**2),b*(a*x+b*y)/(a**2+b**2))
    
    #perpendicular vector
    p2=(x-p1[0],y-p1[1])
    return [p1[0]-p2[0],p1[1]-p2[1]]

def almostPos(tuple1,tuple2):
    #check if the positions as almost the same
    (x0,y0)=tuple1
    (x1,y1)=tuple2
    return (abs(x0-x1)<10**(-5)) and (abs(y0-y1)<10**(-5))

def hitTheLine(data):
    #check if the ball hit the line
    (distToLine,intersectPt)=centerToLineDist(data)
    interX=intersectPt[0]
    return (distToLine<=data.char.radi and interX<=data.lineStart[0]and 
            interX>=data.lineEnd[0])

def centerToLineDist(data):
    if data.lineVect[0]!=0 and data.lineVect[1]!=0:
        lineSlope1=data.lineVect[1]/data.lineVect[0]
        lineSlope2=(-1)/(data.lineVect[1]/data.lineVect[0])
        b1=data.lineStart[1]-lineSlope1*data.lineStart[0]
        b2=data.char.center[1]-lineSlope2*data.char.center[0]
        
        sectPtX=(b2-b1)/(lineSlope1-lineSlope2)
        sectPtY=lineSlope1*sectPtX+b1
        sectPt=(sectPtX,sectPtY)
    elif data.lineVect[0]==0:
        sectPt=(data.char.center[0],data.lineStart[1])
    else:
        sectPt=(data.lineStart[0],data.char.center[1])
    
    xDist=sectPt[0]-data.char.center[0]
    yDist=sectPt[1]-data.char.center[1]
    dist=math.hypot(xDist,yDist)
    return (dist,sectPt)

#Part of motionDetection is cited from:
#http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
#cited at the bejining    
def objectMoving(data):
    points=diffImg(data.t_minus, data.t, data.t_plus)
    ceil=55
    value = ceil
    
    #Check if all nums less than ceil--> nothing moves-->corner detection
    #Check if all nums more than ceil--> sthing is moving-->motion detection
    for line in points:
        value = max(value,max(line))
        
    data.t_minus = data.t
    data.t = data.t_plus
    data.t_plus = cv2.cvtColor(data.cap.read()[1], cv2.COLOR_RGB2GRAY)
    return value > ceil

def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)

#cited at the begining
#CornerDetection is cited from:
#https://www.youtube.com/watch?v=IXyO2O-I2bs
def cornerDetection(data):
    result=[]
    gray = cv2.cvtColor(data.frame,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    
    #The four parameters are image, corners,quality level and min distance.   
    corners=cv2.goodFeaturesToTrack(gray,10,0.02,10)
    corners=np.int0(corners)
    
    for corner in corners:
        (x,y)=corner.ravel()
        if x>=0 and x<=data.width and y>=0 and y<=data.height:
            if not inChar(data,x,y):
                result.append((x,y))
    
    return result

def inChar(data,x,y):
    distX=x-data.char.center[0]
    distY=y-data.char.center[1]
    return math.hypot(distX,distY)<=1.2*data.char.radi

def playRedrawAll(canvas, data):
    canvas.create_image(0, 0, anchor=NW, image=data.imgtk)
    
    #draw the detected corners and line
    # # if data.corners!=None:
    # #     for corner in data.corners:
    # #         x,y=corner[0],corner[1]
    # #         canvas.create_oval(x-2,y-2,x+2,y+2,fill='red')
    # # if data.lineVect!=None:
    # #     canvas.create_line(data.lineStart[0],data.lineStart[1],
    # #                     data.lineEnd[0],data.lineEnd[1],
    # #                        fill='green',width=10)
    #draw stars
    for star in data.stars:
        star.draw(canvas)
    #draw bomb
    for bomb in data.bombs:
        bomb.draw(canvas)
    
    if data.explodeLoc!=[]:
        for explosion in data.explodeLoc:
            explosion.draw(canvas)
    
    if data.moveStars!=[]:
        for stars in data.moveStars:
            for star in stars:
                star.draw(canvas)
    
    #draw character
    data.char.drawChar(canvas)
    
    drawUI(canvas,data)

def drawUI(canvas,data):
    #draw button
    buttonColor=rgbString(170,210,201)
    buttonMargin=0.1*data.helpKeyW
    #help button
    (buttonX0,buttonY0,buttonX1,buttonY1)=buttonBound(data.helpKeyX,
                                                      data.topLeftY,
                                                      data.helpKeyW,
                                                      data.helpKeyH)
    canvas.create_rectangle(buttonX0,buttonY0,buttonX1,buttonY1,
                            fill=buttonColor,width=0)
    canvas.create_rectangle(buttonX0+buttonMargin,buttonY0+buttonMargin,
                            buttonX1-buttonMargin,buttonY1-buttonMargin,
                            fill=None,outline='white',width=1)
    canvas.create_text(data.helpKeyX,data.topLeftY,text='HELP',
                       font='Helvetica 10 bold',fill='white')
    #pause button
    (pauseX0,pauseY0,pauseX1,pauseY1)=buttonBound(data.pauseKeyX,
                                                  data.topLeftY,
                                                  data.pauseKeyW,
                                                  data.pauseKeyH)
    canvas.create_rectangle(pauseX0,pauseY0,pauseX1,pauseY1,
                            fill=buttonColor,width=0)
    canvas.create_rectangle(pauseX0+buttonMargin,pauseY0+buttonMargin,
                            pauseX1-buttonMargin,pauseY1-buttonMargin,
                            fill=None,outline='white',width=1)
    canvas.create_line(data.pauseKeyX-data.helpKeyW/6,
                       data.topLeftY-data.helpKeyH/3,
                       data.pauseKeyX-data.helpKeyW/6,
                       data.topLeftY+data.helpKeyH/3,fill='white',width=5)
    canvas.create_line(data.pauseKeyX+data.helpKeyW/6,
                       data.topLeftY-data.helpKeyH/3,
                       data.pauseKeyX+data.helpKeyW/6,
                       data.topLeftY+data.helpKeyH/3,fill='white',width=5)
    #draw Num
    numColor=rgbString(255,213,33)
    canvas.create_text(data.starNumX,data.topLeftY,text=data.starNum,
                       font='Helvetica 10 bold',fill=numColor)
    #draw star
    data.symbolStar.draw(canvas)

#rgbString cited from 15112 graphics
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def buttonBound(x,y,w,h):
    x0,y0=x-w,y-h
    x1,y1=x+w,y+h
    return x0,y0,x1,y1
    
##Character Class
class Ninja(object):
    def __init__(self,x=0,y=0):
        self.center=[x,y]
        self.radi=20
        self.dir=[12,12]
        self.color='gray50'
       
        self.bullets=None
        self.bulletH=2.5
        self.bulletW=4
        self.shootDir=0
        
    def fall(self):
        self.center[0]+=self.dir[0]
        self.center[1]+=self.dir[1]
        
    def shoot(self):
        self.bullets[0]+=30*self.shootDir
      
    def drawChar(self,canvas):
        if self.bullets!=None:
            drawBullet(self,canvas)

        (x0,y0)=(self.center[0]-self.radi,self.center[1]-self.radi)
        (x1,y1)=(self.center[0]+self.radi,self.center[1]+self.radi)
        margin=3
        
        #draw white backcolor
        canvas.create_oval(x0-margin,y0-margin,x1+margin,y1+margin,
                           fill='white',width=0)
        #draw body
        canvas.create_oval(x0,y0,x1,y1,fill=self.color,width=2)
        
        #draw highlight
        r=self.radi*0.75
        #start from 10 degree
        s0=self.center[0]+r*math.cos(math.radians(15))
        s1=self.center[1]-r*math.sin(math.radians(15))
        #mid at 45 degree
        m0=self.center[0]+r*math.cos(math.radians(45))
        m1=self.center[1]-r*math.sin(math.radians(45))
        #end at 75 degree
        e0=self.center[0]+r*math.cos(math.radians(75))
        e1=self.center[1]-r*math.sin(math.radians(75))
        #circle at 0 degree
        cx=self.center[0]+r
        cy=self.center[1]
        
        canvas.create_line(s0,s1,m0,m1,e0,e1,smooth=True,fill='white',width=4)
        canvas.create_oval(cx-2,cy-2,cx+2,cy+2,fill='white',width=0)

def drawBullet(self,canvas):
    color=rgbString(232,43,39)
    margin=2
    x0,y0=self.bullets[0]-self.bulletW, self.bullets[1]-self.bulletH
    x1,y1=self.bullets[0]+self.bulletW, self.bullets[1]+self.bulletH
    canvas.create_oval(x0-margin,y0-margin,x1+margin,y1+margin,
                       fill='white',width=0)
    canvas.create_oval(x0,y0,x1,y1,fill=color,width=0)

class Star(object):
    def __init__(self,x=0,y=0,color='#ffd521',angle=0,radi=12):
        self.color=color
        self.x=x
        self.y=y
        self.radi=radi
        self.lightRadi=self.radi+2
        self.lightDist=self.lightRadi+4
        self.angle=angle
        self.mar=1.3*self.radi
    
    def draw(self,canvas):
        #first triangle
        #left Pt
        leftX=self.x+self.radi*math.cos(math.radians(150+self.angle))
        leftY=self.y-self.radi*math.sin(math.radians(150+self.angle))
        back1X=self.x+self.mar*math.cos(math.radians(150+self.angle))
        back1Y=self.y-self.mar*math.sin(math.radians(150+self.angle))
        #right Pt
        rightX=self.x+self.radi*math.cos(math.radians(30+self.angle))
        rightY=self.y-self.radi*math.sin(math.radians(30+self.angle))
        back2X=self.x+self.mar*math.cos(math.radians(30+self.angle))
        back2Y=self.y-self.mar*math.sin(math.radians(30+self.angle))
        #down Pt
        downX=self.x+self.radi*math.sin(math.radians(self.angle))
        downY=self.y+self.radi*math.cos(math.radians(self.angle))
        back3X=self.x+self.mar*math.sin(math.radians(self.angle))
        back3Y=self.y+self.mar*math.cos(math.radians(self.angle))
        
        #second triangle
        #top Pt
        topX=self.x-self.radi*math.sin(math.radians(self.angle))
        topY=self.y-self.radi*math.cos(math.radians(self.angle))
        back4X=self.x-self.mar*math.sin(math.radians(self.angle))
        back4Y=self.y-self.mar*math.cos(math.radians(self.angle))
        #down left Pt
        downLeftX=self.x-self.radi*math.sin(math.radians(60-self.angle))
        downLeftY=self.y+self.radi*math.cos(math.radians(60-self.angle))
        back5X=self.x-self.mar*math.sin(math.radians(60-self.angle))
        back5Y=self.y+self.mar*math.cos(math.radians(60-self.angle))
        #down right Pt
        downRightX=self.x+self.radi*math.sin(math.radians(60+self.angle))
        downRightY=self.y+self.radi*math.cos(math.radians(60+self.angle))
        back6X=self.x+self.mar*math.sin(math.radians(60+self.angle))
        back6Y=self.y+self.mar*math.cos(math.radians(60+self.angle))
        
        canvas.create_polygon(back1X,back1Y,back2X,back2Y,back3X,back3Y,
                              fill='white',width=0)
        canvas.create_polygon(back4X,back4Y,back5X,back5Y,back6X,back6Y,
                              fill='white',width=0)
        canvas.create_polygon(leftX,leftY,rightX,rightY,downX,downY,
                              fill=self.color,width=0)
        canvas.create_polygon(topX,topY,downLeftX,downLeftY,
                              downRightX,downRightY,fill=self.color,width=0)
        #draw light
        for i in range (0,6):
            inX=self.x+self.lightRadi*math.cos(math.radians(i*60+self.angle))
            inY=self.y-self.lightRadi*math.sin(math.radians(i*60+self.angle))
            outX=self.x+self.lightDist*math.cos(math.radians(i*60+self.angle))
            outY=self.y-self.lightDist*math.sin(math.radians(i*60+self.angle))
            
            canvas.create_line(inX,inY,outX,outY,fill=self.color,width=2)

class BonusStar(Star):
    def __init__(self,x=0,y=0,color='#ffd521',angle=0,radi=12):
        super().__init__(x,y,color,angle,radi)
        self.maxDist=60
        self.depth=0
        r=random.randint(self.maxDist//2,self.maxDist)
        angle=random.randint(0,11)*math.pi/6
        self.vector=(r*math.cos(angle),-r*math.sin(angle))
    
    def move(self,x0,x1,y0,y1):
        self.depth+=1
        self.x+=(1/self.depth)*self.vector[0]
        self.y+=(1/self.depth)*self.vector[1]
        if self.x<x0 or self.x>x1 or self.y<y0 or self.y>y1:
            self.x-=(1/self.depth)*self.vector[0]
            self.y-=(1/self.depth)*self.vector[1]

class Bomb(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.radi=10
        self.image=PhotoImage(file='C:/Users/Jessy/Desktop/CMU/2017 Spring/15-112/term project/TP2/bomb.gif')
        
    def draw(self,canvas):
        canvas.create_image(self.x,self.y,image=self.image)
        
class Explosion(object):
    def __init__(self,x,y,depth=1):
        self.num=15
        self.start=[(x,y)]*self.num
        self.depth=depth
        self.steps=[]
        self.radi=30
        self.r=255
        self.g=202
        self.b=36
        for i in range(self.num):
            r=random.randint(self.radi//2,self.radi)
            angle=i*math.pi/6
            vector=(r*math.cos(angle),-r*math.sin(angle))
            self.steps.append(vector)
    
    def explode(self):
        if self.depth==0: pass
        else:
            for i in range (self.num):
                x=self.start[i][0]+(1/self.depth)*self.steps[i][0]
                y=self.start[i][1]+(1/self.depth)*self.steps[i][1]
                self.start[i]=(x,y)
        self.depth+=1
    
    def draw(self,canvas):
        for i in range(self.num):
            (x0,y0)=self.start[i]
            x1=x0+(1/self.depth)*self.steps[i][0]
            y1=y0+(1/self.depth)*self.steps[i][1]
            color=rgbString(self.r,self.g-19*self.depth,self.b)
            canvas.create_line(x0,y0,x1,y1,fill=color,width=2)
        
###help mode
def helpMousePressed(event, data):
    #if pressed the button
    (bX0,bY0,bX1,bY1)=buttonBound(data.width/2,4*data.height/5,
                                  data.bttnW,data.bttnH)
    if event.x>=bX0 and event.x<=bX1 and event.y>=bY0 and event.y<=bY1:
        data.mode='play'
        data.pause=not data.pause

def helpTimerFired(data):
    pass

def helpRedrawAll(canvas, data):
    margin=5
    x0,y0,x1,y1=buttonBound(data.width/2,4*data.height/5,data.bttnW,data.bttnH)
    #draw button
    canvas.create_rectangle(0,0,data.width,data.height,fill='gray85',width=0)
    canvas.create_rectangle(x0,y0,x1,y1,fill='gray70',width=0)
    canvas.create_rectangle(x0+margin,y0+margin,x1-margin,y1-margin,
                            outline='white',width=1)
    canvas.create_text(data.width/2,4*data.height/5,text='Go Back',
                       fill='white',font='Helvetica 20 bold')
    for i in range(len(data.intro)-3):
        canvas.create_text(data.width/2,data.height/4+25*i,text=data.intro[i],
                           fill='gray60',font='Helvetica 10')   


###over mode
def overInit(data):
    data.overBttnW=80
    data.overBttnH=30
    data.highest=getRecord(data.starNum)

def overMousePressed(event, data):
    x0,x1=data.width/2-data.overBttnW,data.width/2+data.overBttnW
    y0,y1=3*data.height/4-data.overBttnH,3*data.height/4+data.overBttnH
    if event.x>=x0 and event.x<=x1 and event.y>=y0 and event.y<=y1:
        data.mode='play'
        playInit(data)

def overTimerFired(data):
    pass

def overRedrawAll(canvas, data):
    margin=5
    x0,x1=data.width/2-data.overBttnW,data.width/2+data.overBttnW
    y0,y1=3*data.height/4-data.overBttnH,3*data.height/4+data.overBttnH
    canvas.create_rectangle(0,0,data.width,data.height,fill='gray85',width=0)
    canvas.create_rectangle(x0,y0,x1,y1,fill='gray70',width=0)
    canvas.create_rectangle(x0+margin,y0+margin,x1-margin,y1-margin,
                            outline='white',width=1)
    canvas.create_text(data.width/2,3*data.height/4,text='TRY AGAIN',
                       fill='white',font='Helvetica 20 bold')   
    canvas.create_text(data.width/2,data.height/3,text='GAME OVER', anchor=N,
                        fill='white',font='Helvetica 40 bold')
    canvas.create_text(data.width/2,data.height/2,
                        text='Highest Score: %d'%data.highest,fill='white',
                        font='Helvetica 15')
    canvas.create_text(data.width/2,data.height/2+25,
                        text='Your Score: %d'%data.starNum,fill='white',
                        font='Helvetica 15')
    
#compare with highest record
def getRecord(curScore):
    preScore=readFile("C:/Users/Jessy/Desktop/CMU/2017 Spring/15-112/term project/TP3/records.txt")
    if int(preScore)>curScore:
        return int(preScore)
    else:
        writeFile("C:/Users/Jessy/Desktop/CMU/2017 Spring/15-112/term project/TP3/records.txt",str(curScore))
        return curScore

#readFile cited from 15112 web notes topic string    
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

#readFile cited from 15112 web notes topic string 
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

#run function cited from barebones setup from 15112 web notes
####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Create root before calling init (so we can create images in init)
    root = Tk()
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 25# milliseconds
    data.cap = cv2.VideoCapture(1)
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    data.cap.release()#Close the camera
    print("bye!")

run(630, 470)