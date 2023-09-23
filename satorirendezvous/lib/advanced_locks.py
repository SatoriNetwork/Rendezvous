''' 
this module it an attempt at a type that contains two locks, allowing reads
to happen simultaneously, but writes must be exclusive to both reads and writes.

since reading twice is such a rare occurance in our case, and since this began 
to get complicated we'll just use a single lock for both reads and writes.

# if self.lock.locked():
#    no writes allowed
#    no reads allowed
# if not self.lock.locked() and self.softLock:
#    no writes allowed
#    reads allowed -> self.softLock = True
# if not self.lock.locked() and not self.softLock:
#    writes allowed -> self.lock.acquire()
#    reads allowed -> self.softLock = True
'''
# class LockableList(Generic[T], List[T]):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.write_lock = threading.Lock() # Lock for writing (exclusive access)
#        self.read_lock = threading.RLock() # Lock for reading (shared access)
#        self.write_condition = threading.Condition(lock=self.write_lock)
#        self.read_condition = threading.Condition(lock=self.read_lock)
#
#    def locked(self):
#        return self.write_lock.locked()
#
#    def unlock(self):
#        return self.write_lock.release()
#
#    def write(self):
#        return self.write_lock.acquire()
#
#    def unwrite(self):
#        return self.write_lock.release()
#
#    def read(self):
#        return self.read_lock.acquire()
#
#    def unread(self):
#        return self.read_lock.release()
#
#    def release_read(self):
#        return self.read_lock.release()
#
#    def __enter__(self):
#        self.write_lock.acquire()
#        return self
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.write_condition.notify_all()
#        self.write_lock.release()
#        return False
#
#    def read_context(self):
#        return ReadLockContext(self.read_lock, self.read_condition, self.write_condition)
#
#    def write_notify(self):
#        with self.write_condition:
#            self.write_condition.notify_all()
#
#
# class ReadLockContext:
#    def __init__(
#        self,
#        lock: threading.RLock,
#        condition: threading.Condition,
#        write_condition: threading.Condition
#    ):
#        self.lock = lock
#        self.condition = condition
#        self.write_condition = write_condition
#
#    def __enter__(self):
#        self.lock.acquire()
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.lock.release()
#        with self.condition:
#            self.condition.notify_all()
#        with self.write_condition:
#            self.write_condition.notify_all()


# here's a modified version of your code that enforces mutual exclusion between
# reading and writing:
# import threading
# from typing import Generic, List, TypeVar
#
# T = TypeVar('T')
#
# class LockableList(Generic[T], List[T]):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.write_lock = threading.Lock()  # Lock for writing (exclusive access)
#        self.read_lock = threading.RLock()   # Lock for reading (shared access)
#        self.write_condition = threading.Condition(lock=self.write_lock)
#        self.read_condition = threading.Condition(lock=self.read_lock)
#        self.readers = 0  # Number of threads holding the read lock
#
#    def locked(self):
#        return self.write_lock.locked() or self.read_lock.locked()
#
#    def unlock(self):
#        return self.write_lock.release()
#
#    def write(self):
#        return self.write_lock.acquire()
#
#    def unwrite(self):
#        return self.write_lock.release()
#
#    def read(self):
#        with self.read_lock:
#            self.readers += 1
#
#    def unread(self):
#        with self.read_lock:
#            self.readers -= 1
#            if self.readers == 0:
#                self.read_condition.notify_all()
#
#    def release_read(self):
#        with self.read_lock:
#            if self.readers > 0:
#                self.readers -= 1
#                if self.readers == 0:
#                    self.read_condition.notify_all()
#
#    def __enter__(self):
#        self.write_lock.acquire()
#        return self
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.write_condition.notify_all()
#        self.write_lock.release()
#        return False
#
#    def read_context(self):
#        return ReadLockContext(self.read_lock, self.read_condition, self.write_condition)
#
#    def write_notify(self):
#        with self.write_condition:
#            self.write_condition.notify_all()
#
# class ReadLockContext:
#    def __init__(
#        self,
#        lock: threading.RLock,
#        condition: threading.Condition,
#        write_condition: threading.Condition
#    ):
#        self.lock = lock
#        self.condition = condition
#        self.write_condition = write_condition
#
#    def __enter__(self):
#        with self.lock:
#            self.condition.wait()  # Wait until no writing is happening
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        with self.lock:
#            self.condition.notify_all()  # Notify waiting writers
#        with self.write_condition:
#            self.write_condition.notify_all()  # Notify waiting writers

# ----------------------------------------------------------------------------------------------------------
# this one might work, and might be the simplest solution:
import threading
from typing import TypeVar, Generic, List, Dict

T = TypeVar('T')


class LockableList(Generic[T], List[T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()  # Lock for exclusive access (write)
        self.condition = threading.Condition(lock=self.lock)
        self.readLock = threading.RLock()  # Lock for shared access (reads)
        self.readCondition = threading.Condition(lock=self.readLock)
        self.read = ReadLockContext(
            self.readLock, self.readCondition, self.lock, self.condition)

    @property
    def readers(self):
        return self.read.readers

    def locked(self):
        return self.lock.locked()

    def unlock(self):
        return self.lock.release()

    def lockup(self):
        return self.lock.acquire()

    def __enter__(self):
        self.readLock.acquire()
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.condition.notify_all()
        self.lock.release()
        self.readCondition.notify_all()
        self.readLock.release()
        return False


class ReadLockContext:
    def __init__(
        self,
        lock: threading.RLock,
        condition: threading.Condition,
        writeLock: threading.Lock,
        writeCondition: threading.Condition,
    ):
        self.lock = lock
        self.condition = condition
        self.writeLock = writeLock
        self.writeCondition = writeCondition
        self.readers = 0

    def __enter__(self):
        self.writeLock.acquire()
        self.lock.acquire()
        self.writeLock.release()
        self.readers += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.condition.notify_all()
        self.lock.release()
        self.readers -= 1
        return False

# ----------------------------------------------------------------------------------------------------------
# import threading
#
# class ReadWriteLock:
#    ''' A lock object that allows many simultaneous read locks, but
#    only one write lock. '''
#
#    def __init__(self, withPromotion=False):
#        self._read_ready = threading.Condition(threading.RLock())
#        self._readers = 0
#        self._writers = 0
#        self._promote = withPromotion
#        self._readerList = []  # List of Reader thread IDs
#        self._writerList = []  # List of Writer thread IDs
#
#    def acquire_read(self):
#        # logging.debug("RWL : acquire_read()")
#        '''
#        Acquire a read lock. Blocks only if a thread hasacquired the write lock.
#        '''
#        self._read_ready.acquire()
#        try:
#            while self._writers > 0:
#                self._read_ready.wait()
#            self._readers += 1
#        finally:
#            self._readerList.append(threading.get_ident())
#            self._read_ready.release()
#
#    def release_read(self):
#        # logging.debug("RWL : release_read()")
#        ''' Release a read lock. '''
#        self._read_ready.acquire()
#        try:
#            self._readers -= 1
#            if not self._readers:
#                self._read_ready.notifyAll()
#        finally:
#            self._readerList.remove(threading.get_ident())
#            self._read_ready.release()
#
#    def acquire_write(self):
#        # logging.debug("RWL : acquire_write()")
#        '''
#        Acquire a write lock. Blocks until there are no acquired read or write
#        locks.
#        '''
#        self._read_ready.acquire()   # A re-entrant lock lets a thread re-acquire the lock
#        self._writers += 1
#        self._writerList.append(threading.get_ident())
#        while self._readers > 0:
#            # promote to write lock, only if all the readers are trying to promote to writer
#            # If there are other reader threads, then wait till they complete reading
#            if self._promote and threading.get_ident() in self._readerList and set(self._readerList).issubset(set(self._writerList)):
#                break
#            else:
#                self._read_ready.wait()
#
#    def release_write(self):
#        # logging.debug("RWL : release_write()")
#        ''' Release a write lock. '''
#        self._writers -= 1
#        self._writerList.remove(threading.get_ident())
#        self._read_ready.notifyAll()
#        self._read_ready.release()
#
# class ReadRWLock:
#    # Context Manager class for ReadWriteLock
#    def __init__(self, rwLock):
#        self.rwLock = rwLock
#
#    def __enter__(self):
#        self.rwLock.acquire_read()
#        return self         # Not mandatory, but returning to be safe
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.rwLock.release_read()
#        return False        # Raise the exception, if exited due to an exception
#
# class WriteRWLock:
#    # Context Manager class for ReadWriteLock
#    def __init__(self, rwLock):
#        self.rwLock = rwLock
#
#    def __enter__(self):
#        self.rwLock.acquire_write()
#        return self         # Not mandatory, but returning to be safe
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.rwLock.release_write()
#        return False        # Raise the exception, if exited due to an exception
#
# ----------------------------------------------------------------------------------------------------------
