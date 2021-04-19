import numpy as np
import cv2
import time
import system
import function
import facerecognizer


# sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
# sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
# sudo apt-get install libxvidcore-dev libx264-dev
# sudo apt-get install libgtk2.0-dev libgtk-3-dev
# sudo apt-get install libatlas-base-dev gfortran
# sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev -y
# sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
# sudo apt-get install libxvidcore-dev libx264-dev -y
# sudo apt-get install libgtk2.0-dev libgtk-3-dev -y
# sudo apt-get install libatlas-base-dev gfortran -y
# sudo apt-get install libhdf5-dev libhdf5-serial-dev
# sudo apt install libopenexr-dev
# sudo apt install libqtgui4
# sudo apt install libqt4-test

# pip3 install opencv-contrib-python==4.1.0.25
# sudo pip3 install smbus
# sudo pip3 install rpi_ws281x
class Vision(object):

    def open(self, ch=0, width=640, height=480):
        self.cap = cv2.VideoCapture(ch)
        print("video")
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        self.recognizer = facerecognizer.FaceRecognizer()
        self.result = None
        print("open : " + str(width) + " " + str(height))
        print("open : " + str(self.width) + " " + str(self.height))

    def close(self):
        if self.cap:
            self.cap.release()

    def grab(self, cnt=5):
        if not self.cap:
            return False, None
        if not self.cap.isOpened():
            return False, None
        for i in range(0, cnt - 1):
            self.cap.read()
        return self.cap.read()

    def rescale_frame(self, frame, percent=75):
        width = int(frame.shape[1] * percent/ 100)
        height = int(frame.shape[0] * percent/ 100)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

    def write_img(self, path):
        try:
            if self.result is None:
                return
            cv2.imwrite(path, self.result)
        except Exception as e:
            print('except: '+ str(e)) 

    def run(self):
        try:
            success, frame = self.grab()
            if not success:
                return
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            result, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if not result:
                return
            cv2.imwrite('result.jpg', threshold)
        except Exception as e:
            print('except: '+ str(e))

    def blob(self):
        success, frame = self.grab()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        result, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = 0
        params.maxThreshold = 255
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 100
        # Filter by Circularity
        params.filterByCircularity = False
        params.minCircularity = 0.1
        # Filter by Convexity
        params.filterByConvexity = False
        params.minConvexity = 0.87
        # Filter by Inertia
        params.filterByInertia = False
        params.minInertiaRatio = 0.01
        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(threshold)
        im_with_keypoints = cv2.drawKeypoints(threshold, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self.show("test", im_with_keypoints)

    def labeling(self):
        success, frame = self.grab()
        if not success:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        result, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if False:
            result, labels = cv2.connectedComponents(threshold)

            # Map component labels to hue val
            label_hue = np.uint8(179*labels/np.max(labels))
            blank_ch = 255*np.ones_like(label_hue)
            labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

            # cvt to BGR for display
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

            # set bg label to black
            labeled_img[label_hue==0] = 0

            self.show('labeled.png', labeled_img)
        else:
            result, labels, stats, centroids = cv2.connectedComponentsWithStats(threshold)
            for x, y, w, h, cnt in stats:
                if (h, w) < frame.shape:
                    cv2.rectangle(frame, (x,y,w,h), (0,255,0), 1)
            self.show('test', frame)

            threshold_not = cv2.bitwise_not(threshold)
            result, labels, stats, centroids = cv2.connectedComponentsWithStats(threshold_not)
            for x, y, w, h, cnt in stats:
                if (h, w) < frame.shape:
                    cv2.rectangle(frame, (x,y,w,h), (255,0,0), 1)
            self.show('test', frame)
            self.show('binary', threshold)
            
    def live(self):
        success, frame = self.grab()
        if not success:
            return
        r_frame = self.rescale_frame(frame, 50)
        self.show('live', r_frame)

    def show(self, name, img):
        if system.is_raspi() :
            return
        cv2.imshow(name, img)
    
    def regist_face(self, name):
        cnt = 0
        while True:
            success, frame = self.grab()
            if not success:
                pass
            if self.recognizer.face_regsitor(frame, name, cnt) :
                cnt += 1
            if cnt >= 100:
                break
            time.sleep(0.1)

    def thread_loop(self):
        self.regist_face('heesung')
        self.recognizer.train_from_file()
        while True:
            success, frame = self.grab()
            if not success:
                continue
            self.result, x, y = self.recognizer.face_recognize(frame)
            time.sleep(0.1)


    def thread_start(self):
        function.asyncf(self.thread_loop)

vision = Vision()
if __name__ == '__main__':
    print("start")
    # vision.open('rtsp://eigger:rtsph264@192.168.100.103:8554/unicast')
    vision.open(0)
    try:
        while True:
            try :
                vision.live()
                cv2.waitKey(1)
            except KeyboardInterrupt:
                print("exit")
                break
            except Exception as e:
                print('except: '+ str(e))
            
                
        cv2.destroyAllWindows()
        vision.close()
    except Exception as e:
        print('except: '+ str(e))
