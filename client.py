import zmq
import sys
import pickle
import random

def master_connection(context, master_link, file_name, UpDown):
    master_socket = context.socket(zmq.REQ)
    master_socket.connect ("tcp://{link}".format(link = master_link))
    master_socket.send_pyobj((file_name, UpDown))
    print("Request sent to master datahandler")
    #recieve port from master
    datakeeper_link = master_socket.recv_string()
    print("datakeeper link: " + datakeeper_link)
    return datakeeper_link

def datakeeper_connection(context, datakeeper_link):
    datakeeper_socket = context.socket(zmq.PAIR)
    datakeeper_socket.connect ("tcp://{link}".format(link = datakeeper_link))
    return datakeeper_socket
    
def upload(datakeeper_socket, file_name):
    with open(file_name, "rb") as video_file:
        video = video_file.read()
    msg = datakeeper_socket.send(pickle.dumps(video))
    return
    
def download(datakeeper_socket, file_name):
    video = pickle.loads(datakeeper_socket.recv())
    with open(file_name, "wb") as video_file:
        video_file.write(video)
    return
    
def main():
    _, master_ip, master_port, ports_count, file_name, UpDown = sys.argv
    context = zmq.Context()
    master_port = random.randrange(int(master_port), int(master_port) + int(ports_count))
    master_link = master_ip + ":" + str(master_port)
    datakeeper_link = master_connection(context, master_link, file_name, UpDown)

    if not datakeeper_link:
        print('No empty ports on the server')
        return
    datakeeper_socket = datakeeper_connection(context, datakeeper_link)
    #send request to data keeper
    datakeeper_socket.send(pickle.dumps((file_name, UpDown)))
    if(UpDown == "0"):
        upload(datakeeper_socket, file_name)
    else:
        download(datakeeper_socket, file_name)
    datakeeper_socket.disconnect("tcp://{link}".format(link = datakeeper_link))
    
if __name__ == '__main__':
    main()