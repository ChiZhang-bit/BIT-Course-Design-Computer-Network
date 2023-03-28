import threading
from queue import Queue
import subprocess
import os
import time

tasks = Queue()
working_thread = list()

sema=threading.Semaphore()


class worker(threading.Thread):
    def __init__(self, log_name):
        self.file_handle = None
        self.socket = None
        self.proc = None
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

        self.log_name = log_name
        self.msg = None
        self.status_code = -1

    def restart(self):
        if (self.file_handle != None):
            self.file_handle.close()
            self.file_handle = None
        if (self.socket != None):
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print("socket error:", e)
            self.socket = None
        if (self.proc != None and self.proc.poll() != None):
            self.proc.kill()
            self.proc = None

    def get(self, file_name, is_head=False):
        if (os.path.isfile(file_name)):
            file_suffix = file_name.split('.')
            file_suffix = file_suffix[-1].encode()
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/" + file_suffix + b";charset=utf-8\r\n"

            self.status_code = 200
        else:
            content = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html;charset=utf-8\r\n"
            file_name = "404.html"

            self.status_code = 404
        content += b'\r\n'
        self.socket.sendall(content)

        file_size = 0

        if not is_head:
            self.file_handle = open(file_name, "rb")
            for line in self.file_handle:
                self.socket.sendall(line)

            file_size = os.path.getsize(file_name)

        self.write_log(file_size)

    def post(self, file_name, args):
        ## TODO 计算器可能有写小 bug ，在手机访问的时候传入的参数不对，到时候修一修
        command = 'python ' + file_name + ' "' + args + '" "' + self.socket.getsockname(
        )[0] + '" "' + str(self.socket.getsockname()[1]) + '"'
        self.proc = subprocess.Popen(command,
                                     shell=True,
                                     stdout=subprocess.PIPE)
        self.proc.wait()

        file_size = 0

        if (self.proc.poll() == 2):  ## 文件不存在时返回值为2
            content = b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html;charset=utf-8\r\n"
            page = b''
            self.file_handle = open("403.html", "rb")
            for line in self.file_handle:
                page += line
            content += b'\r\n'
            content += page

            self.status_code = 403
        else:
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=utf-8\r\n"
            content += self.proc.stdout.read()

            file_size = os.path.getsize(file_name)
            self.status_code = 200
        self.socket.sendall(content)

        self.write_log(file_size)

    # 日志书写（文件大小）
    def write_log(self, file_size):
        content = self.msg[1].split(":")[1].replace(" ", "")
        content = content + "--"
        content = content + "[" + str(time.localtime().tm_year) + "-" + str(
            time.localtime().tm_mon) + "-" + str(
                time.localtime().tm_mday) + "-" + str(
                    time.localtime().tm_hour) + "-" + str(
                        time.localtime().tm_min) + "-" + str(
                            time.localtime().tm_sec) + "]"
        content = content + " " + self.msg[0].split("/")[0].replace(" ",
                                                                    "") + " "
        content = content + " " + self.msg[0].split(" ")[1].replace(" ",
                                                                    "") + " "
        content = content + str(file_size) + " "
        content = content + str(self.status_code) + " "
        for i in self.msg:
            # print(i)
            # print(i.split(" ")[0])
            if (i.split(" ")[0] == "Referer:"):
                content = content + i.split(" ")[1].replace(" ", "")

        content = content + "\n"
        with open(self.log_name, "a") as f:
            f.write(content)

    def run(self):
        while True:
            self.socket = tasks.get()
            working_thread.append(self)
            sema.release()

            message = self.socket.recv(8000).decode("utf-8")
            message = message.splitlines()

            self.msg = message

            if (message):
                key_mes = message[0].split()
            else:
                self.restart()
                continue
            if (len(key_mes) <= 1):
                self.restart()
                continue
            file_name = "index.html"
            if (key_mes[1] != "/"):
                file_name = key_mes[1][1:]

            working_thread.append(self)
            try:
                if (key_mes[0] == 'GET'):
                    self.get(file_name)
                elif (key_mes[0] == 'POST'):
                    self.post(file_name, message[-1])
                elif (key_mes[0] == 'HEAD'): # 轻量版get
                    self.get(file_name, True)
                else:
                    content = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n"
                    self.socket.sendall(content)
            except Exception as e:
                print("reason:", e) # read a closed file
            self.restart()
            working_thread.remove(self)
            sema.release()
