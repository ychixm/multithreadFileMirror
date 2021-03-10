import queue
import threading
import time

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
            if randint(0, pow(10, 8)) == 42:
                try:
                    local_ftp.connect()
                    local_ftp.get_folder_content("default")
                    local_ftp.disconnect()
                    print("update")
                except local_ftp.all_errors as e:
                    print(e)
                    continue
            continue
        else:
            tmp = m_queue.get()[1]
            # thread kill
            if tmp[0] == "end":
                alive = False
                continue

            if tmp[0] == "create_file":
                try:
                    local_ftp.connect()
                    local_ftp.file_transfer(tmp[1], tmp[2], tmp[3])
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(tmp)
                    print(e)
                    continue
                continue

            if tmp[0] == "create_dir":
                try:
                    local_ftp.connect()
                    local_ftp.create_folder(tmp[1])
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(tmp)
                    print(e)
                    continue
                continue
            if tmp[0] == "remove_dir":
                print(tmp)
                try:
                    local_ftp.connect()
                    local_ftp.remove_folder(tmp[1])
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(tmp)
                    print(e)
                    continue
                continue
            if tmp[0] == "remove_file":
                try:
                    local_ftp.connect()
                    local_ftp.remove_file(tmp[1])
                    local_ftp.disconnect()
                except local_ftp.all_errors as e:
                    print(tmp)
                    print(e)
                    continue
                continue


class ThreadsManager:
    """
    Private list of known command.
    """
    __known_command = ["end", "create_file", "create_dir", "remove_dir", "remove_file"]

    """
    key : command string
    value : priority value
    """
    __priority_values = {"end": 0, "create_file": 3, "create_dir": 1, "remove_dir": 2, "remove_file": 1}

    """
    key : command string
    value : number of argument + 1 (command string in the tuple)
    """
    __number_of_arguments = {"end": 0, "create_file": 4, "create_dir": 2, "remove_dir": 2, "remove_file": 2}

    def __init__(self, credential, number_of_threads):
        """
        We init the queue, and start the number of threads given.

        :param credential: the credential to log in Filezila server.
        :param number_of_threads: the number of thread who will be created
        """
        self.__queue = queue.PriorityQueue()
        self.threads = []
        for i in range(number_of_threads):
            self.threads.append(threading.Thread(target=request_executor, args=(credential, self.__queue,)))
            self.threads[-1].start()

    def __del__(self):
        """
        Send an end command to all the threads to close them..
        """
        for i in range(len(self.threads)):
            self.add_in_queue("end")
        for i in self.threads:
            i.join()

    def add_in_queue(self, data):
        """
        Check if the command is known and add it to the queue, if not print an error.

        :param data: Tuple with command, and data to execute the command
        """

        if data[0] in self.__known_command:
            if len(data) != self.__number_of_arguments[data[0]]:
                print("Number of argument invalid, ", len(data), " given, ", self.__number_of_arguments[data[0]],
                      "needed")
            try:
                self.__queue.put((self.__priority_values[data[0]], data))
            except Exception as e:
                print("Can not put command in __queue : ", data[0], "; exception raised : ", e)
        else:
            print("Unknown_command : ", data[0])
