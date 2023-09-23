''' untyped lockable containers '''
import threading


class Lockable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.condition = threading.Condition(lock=self.lock)

    def locked(self):
        return self.lock.locked()

    def unlock(self):
        return self.lock.release()

    def lockup(self):
        return self.lock.acquire()

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.condition.notify_all()
        self.lock.release()
        return False


class LockableList(Lockable, list):
    pass


class LockableDict(Lockable, dict):
    pass


class Ints(LockableList[int]):
    '''
    ints example
    '''


class IntStr(LockableDict[int, str]):
    '''
    intstr example
    '''

# ints = Ints([1,2,3])
# ints
# ints.locked()
# with ints:
#    ints.append(4)
#    ints.locked()
#
# ints.locked()
# ints
#
#
# intstr = IntStr({1:'a',2:'b',3:'c'})
# intstr
# intstr.locked()
# with intstr:
#    intstr[4] = 'd'
#    intstr.locked()
#
# intstr.locked()
# [x for x in intstr.keys()]  # x: Any
