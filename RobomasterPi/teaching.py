import json

class Teaching(object):
    def __init__(self):
        self.list = [[] for j in range(20)]
        self.read()

    def set(self, idx, teaching):
        self.list[idx] = teaching
        self.write()

    def get(self, idx):
        return self.list[idx]

    def write(self):
        with open("teaching.json", "w") as json_file:
            json.dump(self.list, json_file)

    def read(self):
        try:
            with open("teaching.json", "r") as json_file:
                self.list = json.load(json_file)
                for i in range(0, 20 - len(self.list)):
                    self.list.append([])
        except:
            pass

    
    def size(self):
        return len(self.list)

teaching = Teaching()
