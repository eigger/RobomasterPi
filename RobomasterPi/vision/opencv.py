import numpy as np
import cv2
import imutils
import time
import threading
import multiprocessing as mp

if __name__ == '__main__':
    from facerecognizer import FaceRecognizer
else:
    from .facerecognizer import FaceRecognizer

VIDEO_PORT: int = 40921

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


class OpenCV(object):

    def open(self, ip=0, width=640, height=480):
        self.address = f'tcp://{ip}:{VIDEO_PORT}'
        self.cap = cv2.VideoCapture(self.address)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.result = None
        self.recognizer = FaceRecognizer()
        self.image = None
        self._mu: mp.Lock = mp.get_context('spawn').Lock()
        print("open : " + str(width) + " " + str(height))
        print("open : " + str(self.width) + " " + str(self.height))
        print("fps : " + str(self.cap.get(cv2.CAP_PROP_FPS)))
        print("buffer : " + str(self.cap.get(cv2.CAP_PROP_BUFFERSIZE)))
        thread = threading.Thread(target=self.thread_loop)
        thread.daemon = True
        thread.start()

    def close(self):
        if self.cap:
            self.cap.release()

    def grab(self):
        if not self.cap:
            return False, None
        if not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def rescale_frame(self, frame, percent=75):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        return imutils.resize(frame, width=width)

    def write_img(self, path):
        try:
            if self.result is None:
                return
            cv2.imwrite(path, self.result)
        except Exception as e:
            print('except: ' + str(e))

    def run(self):
        try:
            success, frame = self.grab()
            if not success:
                return
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            result, threshold = cv2.threshold(
                blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if not result:
                return
            cv2.imwrite('result.jpg', threshold)
        except Exception as e:
            print('except: ' + str(e))

    def blob(self):
        success, frame = self.grab()
        if not success:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        result, threshold = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if not result:
            return
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
        im_with_keypoints = cv2.drawKeypoints(threshold, keypoints, np.array(
            []), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self.show("test", im_with_keypoints)

    def labeling(self):
        success, frame = self.grab()
        if not success:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        result, threshold = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if not result:
            return
        if False:
            result, labels = cv2.connectedComponents(threshold)

            # Map component labels to hue val
            label_hue = np.uint8(179*labels/np.max(labels))
            blank_ch = 255*np.ones_like(label_hue)
            labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

            # cvt to BGR for display
            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

            # set bg label to black
            labeled_img[label_hue == 0] = 0

            self.show('labeled.png', labeled_img)
        else:
            result, labels, stats, centroids = cv2.connectedComponentsWithStats(
                threshold)
            for x, y, w, h, cnt in stats:
                if (h, w) < frame.shape:
                    cv2.rectangle(frame, (x, y, w, h), (0, 255, 0), 1)
            self.show('test', frame)

            threshold_not = cv2.bitwise_not(threshold)
            result, labels, stats, centroids = cv2.connectedComponentsWithStats(
                threshold_not)
            for x, y, w, h, cnt in stats:
                if (h, w) < frame.shape:
                    cv2.rectangle(frame, (x, y, w, h), (255, 0, 0), 1)
            self.show('test', frame)
            self.show('binary', threshold)

    def live(self):
        success, frame = self.grab()
        if not success:
            return
        r_frame = self.rescale_frame(frame, 50)
        self.show('live', r_frame)

    def get_image(self):
        with self._mu:
            return self.image

    def show(self, name, img):
        cv2.imshow(name, img)

    def delay(self, millisec):
        cv2.waitKey(millisec)

    def regist_face(self, name, count):
        cnt = 0
        while True:
            success, frame = self.grab()
            if not success:
                pass
            r_frame = self.rescale_frame(frame, 50)
            result = self.recognizer.face_regsitor(r_frame, name, cnt)
            if result is not None:
                self.show("result", result)
                cnt += 1
            if cnt >= count:
                break
            cv2.waitKey(1)
    
    def train_face(self):
        self.recognizer.train_from_file()

    def recognize_face(self, frame):
        return self.recognizer.face_recognize(frame)

    def thread_loop(self):
        while True:
            success, frame = self.grab()
            if success:
                with self._mu:
                    self.image = frame
                    self.show("dbg", frame)
            self.delay(1)
            

opencv = OpenCV()
if __name__ == '__main__':
    print("start")
    opencv.open('rtsp://eigger:rtsph264@192.168.100.103:8554/unicast')
    # f'tcp://{ch}:{VIDEO_PORT}'
    # opencv.open(0)
    # opencv.thread_loop()
    try:
        while True:
            try:
                opencv.live()
                cv2.waitKey(1)
            except KeyboardInterrupt:
                print("exit")
                break
            except Exception as e:
                print('except: ' + str(e))

        cv2.destroyAllWindows()
        opencv.close()
    except Exception as e:
        print('except: ' + str(e))
