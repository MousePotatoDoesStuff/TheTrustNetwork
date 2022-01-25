import socket


def listen(port=1234,mysocket=None):
    if mysocket is None:
        mysocket=socket.socket()
        host=socket.gethostname()
        print(host,port)
        mysocket.bind((host,port))
        print('Y')
        mysocket.listen(1)
        conn,addr=mysocket.accept()
        welcome='Connection established'.encode()
        conn.send(welcome)
        while True:
            msg=conn.recv(1024)
            msg=msg.decode()
            print('Client:'+msg)
            msg2=input('You:').encode()
            conn.send(msg2)



def main():
    listen()
    return


if __name__ == "__main__":
    main()
