from __future__ import print_function
import tkinter
from tkinter import PhotoImage
import cv2
import PIL.Image, PIL.ImageTk
import pyzbar.pyzbar as pyzbar
import numpy as np
import datetime
import tkinter.font as font

temp_boolean=False #when we obtain temperature this will turn True
buzzer_boolean=False#boolean for buzzer control(i.e. On Off)

class App:
    def __init__(self, window, window_title, video_source=0):
        
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.window.geometry('800x600')
        self.temp_int = 97                         #Lines 18,19 will be replaced by code to get
        self.temp ='Temp:'+ str(self.temp_int)+'°F'#temperature from the sensor 

        # get current date
        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = 500, height = 600)
        self.canvas.place(x=280,y=180)
        
        self.canvas1 = tkinter.Canvas(window, width = 500, height = (self.vid.height)*0.3)
        self.canvas1.place(x=280,y=0)
        
        self.canvas2 = tkinter.Canvas(window, width = 170, height = 550)
        self.canvas2.place(x=10,y=60)
        
        img = PhotoImage(file="Atlas_Copco_logo1.png")      
        self.canvas1.create_image(0,0, anchor=tkinter.NW, image=img)
     
        self.button = tkinter.Button(window,
                                text="Click to display temperature(boolean variable change)",
                                command=self.changeText)#Replace this button by just a call
        self.button.place(x=240,y=150)                  #to the changeText function when
                                                        #temperature is read from sensor
        self.canvas2.create_rectangle(10, 260, 150, 400, 
                                outline = "#076BFB", fill = "", 
                                width = 6)
        self.delay = 15
        self.update()
 
        self.window.mainloop()

    def changeText(self):
        global temp_boolean
        temp_boolean=True

    def decode(self,im) : 
    # Find barcodes and QR codes
        decodedObjects = pyzbar.decode(im)
        # Print results
        for obj in decodedObjects:
            data1=obj.data[:6].decode('utf-8')
            if(data1=="emp123"):
                print('hello',data1)
                data=self.temp_int
                if (95<self.temp_int<99):
                        print('Welcome Aboard ',data1)
                else:
                    global buzzer_boolean
                    buzzer_boolean=True
                    print("Hi",data1,"you may not board the bus your temp is",data)
            else:
                self.canvas.create_text(200,20,text="Unidentified QR Code",fill='red',font='helvetica 20')
            break
        return decodedObjects   

    def update(self):
        
        self.myFont = font.Font(family='Helvetica', size=12, weight='bold')
        self.now = datetime.datetime.now()
        self.labeld = tkinter.Label(self.window, text='Date:-'+str(self.now.strftime("%Y-%m-%d ")),fg="#076BFB")
        self.labeld['font']=self.myFont
        self.labeld.place(x=10,y=10)
        
        self.labelt = tkinter.Label(self.window, text='Time:-'+str(self.now.strftime("%H:%M:%S")),fg="#076BFB")
        self.labelt['font']=self.myFont
        self.labelt.place(x=10,y=30)
        
        
        self.text = tkinter.StringVar()
        
        if temp_boolean==False:
            self.text.set("")
        elif temp_boolean==True:
            self.text.set(self.temp)
            
        self.label = tkinter.Label(self.window, textvariable=self.text)
        self.label.place(x=180,y=150)
   
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decodedObjects = self.decode(im)

            for decodedObject in decodedObjects: 
                points = decodedObject.polygon
     
                if len(points) > 4 :
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else : 
                    hull = points;         
                n = len(hull)
                for i in range(n):
                    self.canvas.create_line( hull[i], hull[ (i+1) % n], fill = "blue", 
                            width = 3)

        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")