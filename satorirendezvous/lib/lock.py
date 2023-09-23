import threading
from typing import TypeVar, Generic, List, Dict

T = TypeVar('T')


class LockableList(Generic[T], List[T]):
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

# class Ints(LockableList[int]):
#    '''
#    ints example
#    '''
#
# ints = Ints([1,2,3])
# [x for x in ints] #x: int


K = TypeVar('K')
V = TypeVar('V')


class LockableDict(Generic[K, V], Dict[K, V]):
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


# can't figure out how to properly abstract it with the typing system.
# class Lockable(Generic[T]):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.lock = threading.Lock()
#        self.condition = threading.Condition(lock=self.lock)
#
#    def locked(self):
#        return self.lock.locked()
#
#    def unlock(self):
#        return self.lock.release()
#
#    def lockup(self):
#        return self.lock.acquire()
#
#    def __enter__(self):
#        self.lock.acquire()
#        return self
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.condition.notify_all()
#        self.lock.release()
#        return False
