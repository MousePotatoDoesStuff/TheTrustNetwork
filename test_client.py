import rsa

from node import Node


def main():
    host = 'DESKTOP-46SQ9U6'
    port = 1234
    ik, pk = rsa.newkeys(512)
    print(ik, ik.n,ik.e)
    testnode = Node('Client', ik, pk)
    testnode.set_node('test',host,port,None)
    testnode.request_data_from_node('test','Jake','Sally')
    return


if __name__ == "__main__":
    main()
