import platform
# Linux: Linux
# Mac: Darwin
# Windows: Windows

def is_linux():
    if (platform.system() == 'Linux'):
        return True
    return False

def is_windows():
    if (platform.system() == 'Windows'):
        return True
    return False

def is_mac():
    if (platform.system() == 'Darwin'):
        return True
    return False

def is_raspi():
    if (is_linux()):
        return True
    return False
if __name__ == '__main__':
    print(platform.system())