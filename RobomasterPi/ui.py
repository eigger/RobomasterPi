import tkinter
import tkinter.ttk
import time
import function
from functools import partial
from teaching import teaching
from controller import controller

class UI(object):

    def __init__(self):
        self.window = tkinter.Tk()
        self.window.resizable(False, False)
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.window.geometry(
            "100x100+"+str(int(self.screen_width/2)-50) + "+" + str(int(self.screen_height/2)-50))
        self.label_splash = tkinter.Label(
            self.window, text="Loading", width=10)
        self.label_splash.pack(side="top", fill="both", expand=True)
        self.window.overrideredirect(True)
        self.progressbar=tkinter.ttk.Progressbar(self.window, orient="horizontal", maximum=100, mode="indeterminate")
        self.progressbar.pack(side="top", fill="both", expand=True)
        self.progressbar.start(50)

    def update_teaching_list(self):
        for i in range(0, teaching.size()):
            self.entry_teaching_list[i].delete(0, len(self.entry_teaching_list[i].get()))
        for i in range(0, teaching.size()):
            for j in range(len(teaching.get(i)) - 1, -1, -1):
                self.entry_teaching_list[i].insert(0, str(teaching.get(i)[j]) + " ")

    def teaching_set(self, teaching_idx):
        set_data = []
        for i in range(0, controller.MAX_SERVO_COUNT):
            position = self.entry_servo[i].get()
            set_data.append(position)
        teaching.set(teaching_idx, set_data)
        self.update_teaching_list()

    def teaching_move_to(self, teaching_idx):
        id_list = [i for i in range(0, controller.MAX_SERVO_COUNT)]
        controller.servo_multi_move_to(id_list, teaching.get(teaching_idx))        

    def teaching_move_all(self):
        while True:
            id_list = [i for i in range(0, controller.MAX_SERVO_COUNT)]
            for teaching_idx in range(0, teaching.size()):
                if len(teaching.get(teaching_idx)) == 0:
                    continue
                controller.servo_multi_move_to(id_list, teaching.get(teaching_idx))
            if self.check_repeat.get() == 0:
                break
  

    def teaching_delete(self, teaching_idx):
        teaching.set(teaching_idx, [])
        self.update_teaching_list()

    def move_to(self, id):
        position = self.entry_servo[id].get()
        controller.servo_move_to(id, position)

    def move(self, id, position):
        controller.servo_move(id, position)
        self.update_position()

    def thread_loop(self):
        self.make_main_window()
        self.window.mainloop()

    def splash_update(self):
        self.window.update()

    def make_main_window(self):
        self.label_splash.destroy()
        self.progressbar.destroy()
        self.window.overrideredirect(False)
        self.window.title("Robot Arm")
        self.window.geometry("1280x700+"+str(int(self.screen_width/2) -
                                            640) + "+" + str(int(self.screen_height/2)-350))

        self.frame_left = tkinter.Frame(self.window, relief="solid", bd=2)
        self.frame_left.pack(side="left", fill="both", expand=True)

        self.frame_right = tkinter.Frame(self.window, relief="solid", bd=2)
        self.frame_right.pack(side="right", fill="both", expand=True)

        self.frame_servo = [tkinter.Frame(
            self.frame_left, relief="solid", bd=2) for i in range(controller.MAX_SERVO_COUNT)]
        self.label_servo = [tkinter.Label(
            self.frame_servo[i], text="Servo(" + str(i) + "):", width=10) for i in range(controller.MAX_SERVO_COUNT)]
        self.entry_servo = [tkinter.Entry(
            self.frame_servo[i]) for i in range(controller.MAX_SERVO_COUNT)]
        self.button_move_to = [tkinter.Button(
            self.frame_servo[i], text="Move To", width=10, command=partial(self.move_to, i)) for i in range(controller.MAX_SERVO_COUNT)]
        self.button_move_p = [tkinter.Button(
            self.frame_servo[i], text="Move +0.5", width=10, command=partial(self.move, i, 0.5)) for i in range(controller.MAX_SERVO_COUNT)]
        self.button_move_n = [tkinter.Button(
            self.frame_servo[i], text="Move -0.5", width=10, command=partial(self.move, i, -0.5)) for i in range(controller.MAX_SERVO_COUNT)]
        for i in range(0, controller.MAX_SERVO_COUNT):
            self.frame_servo[i].pack(side="top", fill="both", expand=True)
            self.label_servo[i].pack(side="left")
            self.entry_servo[i].pack(side="left")
            self.button_move_to[i].pack(side="left")
            self.button_move_p[i].pack(side="left")
            self.button_move_n[i].pack(side="left")

        self.listbox = tkinter.Listbox(self.frame_left, selectmode='extended')
        self.listbox.pack(side="bottom", fill="both", expand=True)

        ################################### right
        self.frame_teaching = tkinter.Frame(self.frame_right, relief="solid", bd=2)
        self.frame_teaching.pack(side="top", fill="both", expand=True)
        self.label_teaching = tkinter.Label(
            self.frame_teaching, text="Teaching", width=10)
        self.label_teaching.pack(side="left")
        self.button_teaching_move_all = tkinter.Button(
            self.frame_teaching, text="Move All", width=10, command=partial(function.asyncf, self.teaching_move_all))
        self.button_teaching_move_all.pack(side="left")
        self.check_repeat=tkinter.IntVar()
        self.button_teaching_move_repeat = tkinter.Checkbutton(
            self.frame_teaching, text="Repeat", width=10, variable=self.check_repeat, onvalue=1, offvalue=0) 
        self.button_teaching_move_repeat.pack(side="left")
        
        
        max_teaching_count = teaching.size()
        print(max_teaching_count)
        self.frame_teaching_list = [tkinter.Frame(
            self.frame_right, relief="solid", bd=2) for i in range(max_teaching_count)]
        self.label_teaching_list = [tkinter.Label(
            self.frame_teaching_list[i], text="Teaching(" + str(i) + "):", width=10) for i in range(max_teaching_count)]
        self.entry_teaching_list = [tkinter.Entry(
            self.frame_teaching_list[i], width=25) for i in range(max_teaching_count)]
        self.button_teaching_set = [tkinter.Button(
            self.frame_teaching_list[i], text="Set", width=10, command=partial(self.teaching_set, i)) for i in range(max_teaching_count)]
        self.button_teaching_move_to = [tkinter.Button(
            self.frame_teaching_list[i], text="Move To", width=10, command=partial(self.teaching_move_to, i)) for i in range(max_teaching_count)]
        self.button_teaching_delete = [tkinter.Button(
            self.frame_teaching_list[i], text="Delete", width=10, command=partial(self.teaching_delete, i)) for i in range(max_teaching_count)]
        
        for i in range(0, max_teaching_count):
            self.frame_teaching_list[i].pack(side="top", fill="both", expand=True)
            self.label_teaching_list[i].pack(side="left")
            self.entry_teaching_list[i].pack(side="left")
            self.button_teaching_set[i].pack(side="left")
            self.button_teaching_move_to[i].pack(side="left")
            self.button_teaching_delete[i].pack(side="left")

        self.update_teaching_list()
        self.update_position()

    def update_position(self):
        for i in range(controller.MAX_SERVO_COUNT):
            self.entry_servo[i].insert(0, str(controller.servo_position[i]))
ui = UI()
if __name__ == '__main__':
    controller.open()
    controller.initializeRMS()
    ui.splash_update()
    time.sleep(1)
    ui.thread_loop()
