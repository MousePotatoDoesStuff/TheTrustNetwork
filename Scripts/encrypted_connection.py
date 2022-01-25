import rsa


class enc_conn:
    def __init__(self, socket, conn, send_pkey, recv_skey):
        self.s = socket
        self.c = conn
        self.recv_skey = recv_skey
        self.send_pkey = send_pkey
        return

    def recv(self, size=1024):
        rawmsg = self.s.recv(size)
        msg = rsa.decrypt(rawmsg, self.recv_skey)
        return msg

    def send(self, msg):
        emsg = rsa.encrypt(msg, self.send_pkey)
        self.s.send(emsg)
        return


def main():

    return


if __name__ == "__main__":
    main()
