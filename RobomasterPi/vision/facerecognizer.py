import cv2
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import os.path

class FaceRecognizer(object):

    def __init__(self):
        self.face_path = '.faces'
        self.face_classifier = cv2.CascadeClassifier('.haarcascade_frontalface_default.xml')
        self.train_model = []
        self.train_name = []

    def face_extractor(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)

        if faces is ():
            return None, []

        for(x, y, w, h) in faces:
            cropped_face = img[y:y+h, x:x+w]
            roi = img[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))

        return cropped_face, roi

    def face_detector(self, img, size=0.5):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)

        if faces is ():
            return img, [], 0, 0

        for(x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            roi = img[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))
            center_x = x + (w / 2)
            center_y = y + (h / 2)

        return img, roi, center_x, center_y

    def face_regsitor(self, img, name, idx):
        cropped_face, roi = self.face_extractor(img)
        if cropped_face is not None:
            face = cv2.resize(cropped_face, (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            path = self.face_path + '/' + name
            if not(os.path.isdir(path)):
                os.makedirs(os.path.join(path))

            file_name_path = path + '/user'+str(idx)+'.jpg'
            cv2.imwrite(file_name_path, face)

            cv2.putText(face, str(idx), (50, 50),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Face Cropper', face)
            print('save: ' + file_name_path)
            return True
        else:
            return False

    def train_from_file(self):
        dir_list = os.listdir(self.face_path)
        for dir in dir_list:
            data_path = self.face_path + '/' + dir + '/'
            if not(os.path.isdir(data_path)):
                continue
            print('path : ' + data_path)
            onlyfiles = [f for f in listdir(
                data_path) if isfile(join(data_path, f))]
            Training_Data, Labels = [], []
            for i, files in enumerate(onlyfiles):
                image_path = data_path + onlyfiles[i]
                images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                Training_Data.append(np.asarray(images, dtype=np.uint8))
                Labels.append(i)

            Labels = np.asarray(Labels, dtype=np.int32)
            model = cv2.face.LBPHFaceRecognizer_create()
            model.train(np.asarray(Training_Data), np.asarray(Labels))

            self.train_model.append(model)
            self.train_name.append(dir)
            print(str(dir) + " Model Training Complete!!!!!")

    def face_recognize(self, img):
        image, face, center_x, center_y = self.face_detector(img)
        max_confidence = 0
        face_name = ''
        h,w = image.shape[:2]
        result_x = 0
        result_y = 0
        for i in range(0, len(self.train_model), 1):
            model = self.train_model[i]
            name = self.train_name[i]
            try:
                face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                result = model.predict(face_gray)

                if result[1] < 500:
                    confidence = int(100*(1-(result[1])/300))
                    if confidence > max_confidence:
                        max_confidence = confidence
                        face_name = name
            except:
                pass
        if len(face_name) > 0:
            display_string = str(max_confidence) + '% Confidence it is ' + face_name
            # cv2.line(image, (int(center_x), int(center_y)), (int(w/2),int(h/2) ), (255,0,0),1)
            result_x = w/2 - center_x
            result_y = h/2 - center_y
        else:
            display_string = 'not detected face'
        cv2.putText(image, display_string, (int(center_x-100), int(center_y - 100)),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (250, 120, 255), 2)
        cv2.imshow('Face Cropper', image)
        return image, result_x, result_y

if __name__ == '__main__':
    recognizer = FaceRecognizer()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture('rtsp://eigger:rtsph264@192.168.0.211:8554/unicast')
    count = 0
    name = 'heesung'
    while True:
        ret, frame = cap.read()
        if recognizer.face_regsitor(frame, name, count) == True:
            count += 1
        if count > 100:
            break
        cv2.waitKey(1)

    recognizer.train_from_file()

    while True:
        ret, frame = cap.read()
        recognizer.face_recognize(frame)

        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()
