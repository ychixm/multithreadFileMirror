import queue
import threading
from talk_to_ftp import TalkToFTP
from random import randint


def request_executor(credential, m_queue):
    """
    the function execute commands from the talk_to_ftp class
    this function is make to be run in a thread, while a "end" has not been send the thread wont stop.

    :param credential: the credential to log in Filezila server.
    :param m_queue: a synchronized queue where the command are placed.
    """
    local_ftp = TalkToFTP(credential)
    # TalkToFTP("localhost,admin,admin,default")

    alive = True
    while alive:
        if m_queue.empty():
            continue
            # requete ping
            # faire un chrono plutot ?
        else:
            tmp = m_queue.get()
            # thread kill
            if tmp[0] == "end":
                alive = False
                continue

            if tmp[0] == "file_transfer":
                try:
                    local_ftp.connect()
                    local_ftp.file_transfer(tmp[1], tmp[2], tmp[3])
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(e)
                    continue
                continue

            if tmp[0] == "create_dir":
                try:
                    local_ftp.connect()
                    local_ftp.create_folder(tmp[1])
                    # local_ftp.create_folder(srv_full_path)
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(e)
                    continue
                continue


class ThreadsManager:
    # Private list of known command.
    __known_command = ["end", "file_transfer", "create_dir"]

    def __init__(self, credential, number_of_threads):
        """
        We init the queue, and start the number of threads given.

        :param credential: the credential to log in Filezila server.
        :param number_of_threads: the number of thread who will be created
        """
        self.__queue = queue.Queue()
        self.threads = []
        for i in range(number_of_threads):
            self.threads.append(threading.Thread(target=request_executor, args=(credential, self.__queue,)))
            self.threads[-1].start()

    def __del__(self):
        """
        Send an end command to all the threads to close them..
        """
        for i in range(len(self.threads)):
            self.__queue.put(("end",))
        for i in self.threads:
            i.join()

    def add_in_queue(self, data):
        """
        Check if the command is known and add it to the queue, if not print an error.

        :param data: Tuple with command, and data to execute the command
        """
        if data[0] in self.__known_command:
            try:
                self.__queue.put(data)
            except Exception as e:
                print("Can not put command in __queue : ", data[0], "; exception raised : ", e)
        else:
            print("Unknown_command : ", data[0])
