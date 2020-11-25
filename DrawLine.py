from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog

import imageio
import cv2
from Moto_Detect import detect_moto
import numpy as np




class Window(Frame):
    def __init__(self, master=None):
        # master: para của tk - dùng để vẽ UI
        Frame.__init__(self, master)
        self.master = master
        self.pos = []
        self.line = []
        self.rect = []
        self.master.title("GUI")

        self.pack(fill=BOTH, expand=1) 
        # dùng fill=BOTH (fill theo cả chiều ngang và dọc) và expand để fill các chỗ trống trong wiget

        self.counter = 0

        menu = Menu(self.master)
        self.master.config(menu=menu) # Tạo giao diện menu của tk
        

        # # add menu item
        file = Menu(menu)
        file.add_command(label="Open", command=self.open_file)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label = "Menu",menu = file)

        # # add hình nền
        self.filename = "images/preview.jpg"
        self.imgSize = Image.open(self.filename)
        self.tkimage =  ImageTk.PhotoImage(self.imgSize) #Tham số truyền vào cho ImageTk là image
        self.w, self.h = (1366, 768)
        
        # Dùng canvas của tkinter để vẽ lên hình ảnh, w và h là kích thước khung hình
        self.canvas = Canvas(master = root, width = self.w, height = self.h)
        # chọn vị trí x, y cho hình ảnh, chọn anchor= NW để cho hình ảnh đặt ở vị trí góc bên trái và phía trên (bắt đầu từ vị trí x, y)
        self.canvas.create_image(20, 20, image=self.tkimage, anchor='nw')

        self.canvas.pack() #load các wiget lên parent wiget

    def open_file(self):
        self.filename = filedialog.askopenfilename()

        cap = cv2.VideoCapture(self.filename)

        reader = imageio.get_reader(self.filename) #Đọc tệp  imageio.get_reader(filename, format, mode)

        fps = reader.get_meta_data()['fps']  # lấy data meta ????

        ret, image = cap.read()
        
        # show frame[0] của video đầu vào để vẽ đường thẳng
        cv2.imwrite('images\image0.jpg', image)
        self.show_image('images\image0.jpg')

        # goi ham ve 2 diem
        root.config(cursor="target") 
        self.canvas.bind("<Button-1>", self.imgClick)
    def client_exit(self):
        exit()


    def imgClick(self, event):

        if self.counter < 2:
            x = int(self.canvas.canvasx(event.x))
            y = int(self.canvas.canvasy(event.y))
            self.line.append((x, y))
            self.pos.append(self.canvas.create_line(x - 5, y, x + 5, y, fill="red", tags="crosshair"))
            self.pos.append(self.canvas.create_line(x, y - 5, x, y + 5, fill="red", tags="crosshair"))
            self.counter += 1

        if self.counter == 2:
            #unbinding action with mouse-click
            self.canvas.unbind("<Button-1>") # Nếu đã vẽ đủ 2 điểm thì ngưng gọi event mouse-click
            root.config(cursor="arrow")
            self.counter = 0

            #show created virtual line
            print(self.line)
            print(self.rect)
            img = cv2.imread('images\image0.jpg')
            cv2.line(img, self.line[0], self.line[1], (0, 255, 0), 3)
            cv2.imwrite('images\_afterdraw.jpg', img)
            self.show_image('images\_afterdraw.jpg')


            #image processing
            self.main_process() 
            

            #clearing things
            self.line.clear()
            self.rect.clear()
            for i in self.pos:
                self.canvas.delete(i)

    
    def show_image(self, frame):
        self.imgSize = Image.open(frame)
        self.tkimage =  ImageTk.PhotoImage(self.imgSize)
        self.w, self.h = (1366, 768)

        self.canvas.destroy()

        self.canvas = Canvas(master = root, width = self.w, height = self.h)
        self.canvas.create_image(0, 0, image=self.tkimage, anchor='nw')
        self.canvas.pack()


    def preprocess_input(self, image, net_h, net_w):
        new_h, new_w, _ = image.shape

        # determine the new size of the image
        if (float(net_w)/new_w) < (float(net_h)/new_h):
            new_h = (new_h * net_w)/new_w
            new_w = net_w
        else:
            new_w = (new_w * net_h)/new_h
            new_h = net_h

        # resize the image to the new size
        resized = cv2.resize(image[:,:,::-1]/255., (int(new_w), int(new_h)))

        # embed the image into the standard letter box
        new_image = np.ones((net_h, net_w, 3)) * 0.5
        new_image[int((net_h-new_h)//2):int((net_h+new_h)//2), int((net_w-new_w)//2):int((net_w+new_w)//2), :] = resized
        new_image = np.expand_dims(new_image, 0)

        return new_image
    net_h, net_w = 416, 416
    def main_process(self):

        video_src = self.filename

        cap = cv2.VideoCapture(video_src)
        # convert to a Movie
        reader = imageio.get_reader(video_src)
        fps = reader.get_meta_data()['fps']    
        writer = imageio.get_writer('output\output1.mp4', fps = fps)
            
        j = 1



        while True:
            ret, image1 = cap.read()
            if (type(image1) == type(None)):
                writer.close()
                break

            
            # new_image = self.preprocess_input(image1, self.net_h, self.net_w)
            # haaaa
            # det = detect_moto(image1)
            # image1 = det.run(image1)
            
            writer.append_data(image1)

            cv2.imshow('Nhan dien xe vi pham vuot vach den do', image1)
            
            print(j)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                writer.close()
                break

            j = j+1

        cv2.destroyAllWindows()




root = Tk()
app = Window(root)
root.geometry("%dx%d"%(700, 430))
root.title("Nhan dien xe vi pham")

root.mainloop()