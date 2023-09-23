import threading

# Define the LockableList
lockable_list = LockableList()


def test_read():
    def reader_thread():
        with lockable_list.read:
            print(f"Read thread {threading.current_thread().name} reading.")

    # Start multiple reader threads
    reader_threads = []
    for i in range(3):
        reader_thread = threading.Thread(
            target=reader_thread, name=f"Reader-{i + 1}")
        reader_threads.append(reader_thread)
        reader_thread.start()

    for reader_thread in reader_threads:
        reader_thread.join()


def test_write():
    def writer_thread():
        with lockable_list:
            print(f"Write thread {threading.current_thread().name} writing.")
            # Simulate a write operation
            lockable_list.append(threading.current_thread().name)

    # Start multiple writer threads
    writer_threads = []
    for i in range(2):
        writer_thread = threading.Thread(
            target=writer_thread, name=f"Writer-{i + 1}")
        writer_threads.append(writer_thread)
        writer_thread.start()

    for writer_thread in writer_threads:
        writer_thread.join()


def main():
    # Test simultaneous reads
    print("Simultaneous Reads Test:")
    test_read()

    # Test exclusive writes
    print("\nExclusive Writes Test:")
    test_write()


if __name__ == "__main__":
    main()
