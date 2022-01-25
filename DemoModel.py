import threading
import random
from queue import Queue


class NodeModel:
    def __init__(self, name, network, printout=False):
        self.name = name
        self.trustData: dict = {}
        self.linked_nodes = dict()
        self.network = network
        if printout:
            print('Postavljen node {}'.format(name))
        return

    def set_data(self, entity, subject, value, printout=False):
        if entity not in self.trustData:
            self.trustData[entity] = dict()
        log = self.trustData[entity]
        log[subject] = value
        if printout:
            print('Node {}: Faktor povjerenja entiteta {} za {} postavljen na {}'.format(self.name, entity, subject,
                                                                                         value))
        return

    def set_node(self, index, trust, printout=False):
        self.linked_nodes[index] = trust,
        return

    def request_data_from_node(self, index, entity, subject, printout=False):
        self.network: TrustNetworkModel
        if entity not in self.trustData:
            self.trustData[entity] = dict()
        ent = self.trustData[entity]
        if subject not in ent:
            self.network.requests.put((index, entity, subject))
            return None
        return ent[subject]

    def request_data(self, entity, subject, min_trust=0.5, printout=False):
        L = [(self.linked_nodes[e], e) for e in self.linked_nodes]
        L.sort(key=lambda e: e[0])
        while len(L) > 0:
            el = L.pop()
            if el[0] < min_trust:
                break
            data = self.request_data_from_node(el[1], entity, subject, printout=printout)
            if data is not None:
                return data, el[0]


class TrustNetworkModel:
    def __init__(self, size, trust, printout=False):
        self.nodes = [NodeModel(i, self, printout) for i in range(size)]
        self.requests = Queue()
        self.printout = printout
        for i in range(len(trust)):
            E = trust[i]
            for j in range(len(E)):
                if i == j:
                    continue
                self.nodes[i].set_node(j, E[j], printout)
        self.runningThread = False
        return

    def process_requests(self, min_trust=0.5):
        while self.runningThread:
            X = self.requests.get()
            node = X[0]
            node: NodeModel
            node.request_data(X[1], X[2], min_trust, printout=self.printout)
        return

    def set_data(self, index, entity, subject, value):
        node = self.nodes[index]
        node: NodeModel
        node.set_data(entity, subject, value, printout=self.printout)
        return

    def get_data(self, index, entity, subject, value):
        return

    def get_all_trust(self, default=0):
        M = dict()
        for e in self.nodes:
            e: NodeModel
            M[e.name] = e.trustData
        return M


class th(threading.Thread):
    def __init__(self, model, min_trust):
        super().__init__()
        self.model = model
        self.min_trust = min_trust

    def run(self) -> None:
        model: TrustNetworkModel
        self.model.process_requests(self.min_trust)


def runNetworkModelExample():
    mode = int(input('Mode:'))
    if mode == 0:
        trust = [
            [1, 1, 0.7, 0.5, 0.3],
            [0.7, 1, 0.5, 0.3],
            [1, 1, 1],
            [0, 0, 0, 1, 1],
            [1, 0, 0, 0, 1]
        ]
    elif mode == 1:
        trust = [[round(random.random(), 1) for i in range(5)] for j in range(5)]
    else:
        trust = []
        for i in range(5):
            trust.append([float(e) for e in input().replace(' ', '').split(',')])
    model = TrustNetworkModel(5, trust, printout=True)
    printout = True
    opener = None
    while True:
        request = input('>>> ').split(' ')
        r_type = request[0]
        if r_type == 'add_node':
            n = len(model.nodes)
            model.nodes.append(NodeModel(n, model))
        elif r_type == 'set_trust':
            r_ent = int(request[1])
            r_name = int(request[2])
            r_value = float(request[3])
            model.nodes[r_ent].set_node(r_name, r_value, printout=printout)
        elif r_type == 'get_trust':
            r_ent = int(request[1])
            r_name = int(request[2])
            r_trust = float(request[3])
            r_value = model.nodes[r_ent].request_data(r_name, r_trust)
            print(r_value)
        elif r_type == 'run':
            r_trust = float(request[1])
            opener = th(model, r_trust)
            opener.run()
        elif r_type == 'stop':
            model.runningThread = False
        elif r_type == 'toggle_printout':
            model.printout = False
            printout = False


def main():
    runNetworkModelExample()
    return


if __name__ == "__main__":
    main()
