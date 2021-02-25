import queue
import threading
from talk_to_ftp import TalkToFTP
from random import randint

class threads_manager:
    def __init__(self, credential, number_of_threads,):
        self.queue = queue.Queue
        self.threads = []
        for i in number_of_threads:
            self.threads.append(threading.Thread(target=self.request_executor, args=(credential, self.queue,)))

    def __del__(self):
        self.queue.put(("end",))
        for i in self.threads:
            i.join()

    def request_executor(self, credential, m_queue):
        ftp = TalkToFTP(credential)
        alive = True
        while alive:
            if m_queue.empty():
                if randint(0, 20) == 4:
                    # requete ping
                    # faire un chrono plutot ?
            else :
                tmp = m_queue.get()

        #try get in queue ? sur un while
        #exec funct
