import threading

def asyncf(func, *args):
    thread = threading.Thread(target=func, args=(args))
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    print("start")
