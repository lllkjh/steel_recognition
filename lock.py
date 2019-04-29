import threading
import time


class myLock:
    def __init__(self, src):
        self.global_variable = src
        self.glock = threading.Lock()

    # 获取锁的函数(bool取反)
    def inverse_lock_bool(self):
        while 1:
            if self.glock.acquire():
                self.global_variable = not self.global_variable
                self.glock.release()
                break
            else:
                time.sleep(0.0005)

    # 获取锁的函数(判定bool类型变量)
    def get_lock_bool(self):
        while 1:
            if self.glock.acquire():
                if self.global_variable:
                    self.glock.release()
                    return 1
                else:
                    self.glock.release()
                    return 0
            else:
                time.sleep(0.0005)

    # 设置锁的函数(赋值全局变量)
    def set_lock_global(self, src):
        while 1:
            if self.glock.acquire():
                self.global_variable = src
                self.glock.release()
                break
            else:
                time.sleep(0.0005)

    # 设置锁的函数(赋值全局变量)
    def get_lock_global(self):
        tmp = None
        while 1:
            if self.glock.acquire():
                tmp = self.global_variable
                self.glock.release()
                return tmp
            else:
                time.sleep(0.0005)

    # 获取锁的函数(赋值)
    def get_lock(self, dest, src):
        while 1:
            if self.glock.acquire():
                try:
                    dest = src
                finally:
                    self.glock.release()
                    break
            else:
                time.sleep(0.0005)

    # 获取锁的函数(参数为函数)
    def get_lock_func(self, glock_func, *args):
        while 1:
            if self.glock.acquire():
                try:
                    glock_func(*args)
                finally:
                    self.glock.release()
                    break
            else:
                time.sleep(0.0005)

