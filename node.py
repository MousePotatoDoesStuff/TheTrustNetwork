import socket
import rsa, rsa.randnum
import aes


class Node:
    def __init__(self, name, identityKey, publicKey):
        self.name = name
        self.identityKey = identityKey
        self.publicKey = publicKey
        self.trustData: dict = {}
        self.linked_nodes = dict()
        return

    def set_data(self, entity, subject, value):
        if entity not in self.trustData:
            self.trustData[entity] = dict()
        log = self.trustData[entity]
        log[subject] = value
        return

    def set_node(self, name, host, port, publickey=None):
        self.linked_nodes[name] = (host, port, publickey)
        return

    def request_data_from_node(self, node, entity, subject):
        host, port, publickey = self.linked_nodes[node]
        s = socket.socket()
        s.connect((host, port))
        L = s.recv(1024).decode().split(',')
        temp_pk = rsa.key.PublicKey(int(L[0]), int(L[1]))
        aes_key = rsa.randnum.read_random_bits(128)
        enc_aes_key = rsa.encrypt(aes_key, temp_pk)
        s.send(enc_aes_key)

        c_msg = s.recv(1024)
        signature = aes.decrypt(c_msg, aes_key, 1024)
        try:
            rsa.verify(aes_key, signature, publickey)
        except rsa.pkcs1.VerificationError:
            msg = 'Verification failed'
            s.send(aes.encrypt(msg, aes_key, 1024))
            return
        msg = 'ASK {} {}'.format(entity, subject)
        s.send(aes.encrypt(msg, aes_key, 1024))
        s.close()
        return

    def check_for(self, entity, subject):
        if entity in self.trustData:
            log = self.trustData[entity]
        else:
            log = dict()
        return log[subject]

    def ask_for(self, entity, subject):
        res = None
        for e in self.trustData:
            for node in self.linked_nodes:
                self.request_data_from_node(node, entity, subject)
        return

    def set_for(self, entity, subject, value, source):
        if entity in self.trustData:
            log = self.trustData[entity]
        else:
            log = dict()
        log[subject] = value
        return

    def run(self, port=1234):
        mysocket = socket.socket()
        host = socket.gethostname()
        print(host, port)
        mysocket.bind((host, port))
        print('Running listener')
        while True:
            mysocket.listen(1)
            conn, addr = mysocket.accept()

            temp_sk, temp_pk = rsa.newkeys(512)
            msg = '{},{}'.format(temp_pk.n, temp_pk.e)
            conn.send(msg.encode())

            raw = conn.recv(1024)
            L = rsa.decrypt(raw, temp_pk)
            other_pk = rsa.key.PublicKey(int(L[0]), int(L[1]))

            msg = '{},{}'.format(self.publicKey.n, self.publicKey.e)
            conn.send(rsa.encrypt(msg.encode(), other_pk))

            request = conn.recv(1024).decode()
            L = request.split('|')
            s_res = 'INVALID REQUEST'
            if L[0] == 'ASK':
                r_name, r_subject = None, None
                if len(L) < 3:
                    res = 'INVALID REQUEST'
                    s_res = 'INVALID REQUEST'
                else:
                    r_type, r_name, r_subject = tuple(L)
                    if r_subject[0] == '_':
                        res = 'INVALID SUBJECT'
                        s_res = 'INVALID SUBJECT'
                    else:
                        res = self.check_for(r_name, r_subject)
                        s_res = 'None' if res is None else 'R' + res
                conn.send(s_res.encode())
                conn.close()
                if res is None:
                    self.ask_for(r_name, r_subject)
            elif L[0] == 'ANS':
                r_type, r_name, r_subject, r_value, r_asker = tuple(L)
                if r_subject[0] == '_':
                    pass
                else:
                    self.set_for(r_name, r_type, r_value, r_asker)
                conn.close()


def runNode():
    pk, ik = rsa.newkeys(512)
    testnode = Node('Test', ik, pk)
    while True:
        request = input('>>> ').split(' ')
        r_type = request[0]
        if r_type == 'add_node':
            npk = rsa.key.PublicKey(int(request[4]), int(request[5]))
            testnode.set_node(request[1], request[2], int(request[3]), npk)
        elif r_type == 'set_trust':
            r_ent = request[1]
            if r_ent not in testnode.trustData:
                testnode.trustData[r_ent] = dict()
            cur = testnode.trustData[request[1]]
            cur[request[2]] = float(request[3])
        elif r_type == 'get_trust':
            r_ent = request[1]
            if r_ent not in testnode.trustData:
                print('Entity unknown!')
                continue
            cur = testnode.trustData[request[1]]
            if request[2] not in cur:
                print('Data for entity unknown!')
                continue
            print(cur[request[2]])
        elif r_type == 'run':
            testnode.run(int(request[2]))
        elif r_type == 'skey':
            print(testnode.identityKey)
        elif r_type == 'pkey':
            print(testnode.publicKey)


def main():
    runNode()
    return


if __name__ == "__main__":
    main()
