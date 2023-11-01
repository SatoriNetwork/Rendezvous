'''
please note, because of the GIL we don't even need locks as long as we're only
using threads for concurrency. However, in the event that we do want to use
multiprocessing we can take advantage of these locking mechanisms.
'''
import threading
from typing import TypeVar, Generic, List, Dict, Union

T = TypeVar('T')


class LockableList(Generic[T], List[T]):
    def __init__(self, *args, limit: Union[int, None] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if limit is not None and isinstance(limit, int) and limit > 0:
            self.limit = limit
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

    def safeAppend(self, item):
        with self.lock:
            self.append(item)

    def append(self, item):
        # with self.lock: #should be acquired by caller
        if hasattr(self, 'limit') and len(self) >= self.limit:
            self.pop(0)
        super().append(item)


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
