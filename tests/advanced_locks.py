# import threading
# import pytest
# from satorirendezvous.lib.advanced_locks import LockableList

# # Define a fixture to create an instance of LockableList for testing


# @pytest.fixture
# def lockableList():
#     return LockableList()

# # Test basic locking and unlocking


# def test_lock_and_unlock(lockableList):
#     with lockableList:
#         assert lockableList.locked() == True

#     assert lockableList.locked() == False

# # Test simultaneous reads


# def test_simultaneous_reads(lockableList):
#     def read_task(ll):
#         import time
#         with ll.read:
#             time.sleep(1)
#             print(ll.readers)
#             assert ll.readers > 0

#     ll = LockableList()  # use one object for all threads
#     num_threads = 5
#     threads = []

#     for _ in range(num_threads):
#         thread = threading.Thread(target=read_task, args=(ll,))
#         thread.start()
#         threads.append(thread)

#     for thread in threads:
#         thread.join()

#     assert ll.locked() == False


# Test exclusive writes


# def test_exclusive_writes(lockableList):
#     def write_task(lockableList):
#         with lockableList:
#             assert lockableList.locked() == True

#     num_threads = 5
#     threads = []

#     for _ in range(num_threads):
#         thread = threading.Thread(target=write_task, args=(lockableList,))
#         thread.start()
#         threads.append(thread)

#     for thread in threads:
#         thread.join()

#     assert lockableList.locked() == False

# Test simultaneous reads and exclusive writes


# def test_reads_and_writes(lockableList):
#     def read_task(lockableList):
#         with lockableList.read:
#             assert lockableList.locked() == True

#     def write_task(lockableList):
#         with lockableList:
#             assert lockableList.locked() == True

#     num_read_threads = 5
#     num_write_threads = 3
#     read_threads = []
#     write_threads = []

#     for _ in range(num_read_threads):
#         thread = threading.Thread(target=read_task, args=(lockableList,))
#         thread.start()
#         read_threads.append(thread)

#     for _ in range(num_write_threads):
#         thread = threading.Thread(target=write_task, args=(lockableList,))
#         thread.start()
#         write_threads.append(thread)

#     for thread in read_threads:
#         thread.join()

#     for thread in write_threads:
#         thread.join()

#     assert lockableList.locked() == False


# Run the tests
# if __name__ == "__main__":
#    pytest.main()

from satorirendezvous.lib.advanced_locks import LockableList
import multiprocessing
import time


def read_task(lock, shared_list):
    with lock:
        time.sleep(1)  # Simulate some work
        print()
        shared_list.append(1)  # Add an item to the shared list


if __name__ == "__main__":
    lock = multiprocessing.Lock()
    shared_list = multiprocessing.Manager().list()  # Shared list among processes

    num_processes = 5
    processes = []

    for _ in range(num_processes):
        process = multiprocessing.Process(
            target=read_task, args=(lock, shared_list))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    assert len(shared_list) == num_processes
    print("All processes have completed.")
