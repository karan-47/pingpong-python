import socket
import select
import pymysql

header_length = 20
ip = '192.168.0.105'
# ip = '127.0.0.1'
port = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((ip, port))
server_socket.listen()

sockets_list = [server_socket]

clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(header_length)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


u1 = ""
u2 = ""


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            xyz = user["data"].decode("utf-8")
            print(f'Accepted new connection from {client_address[0]}:{client_address[1]} username:{xyz}')
            if u1 == "":
                u1 = '"'+xyz+'"'
            else:
                u2 = '"'+xyz+'"'
            print(u1, u2)


        else:
            message = receive_message(notified_socket)

            if message is False:
                print(f'Closed connection from {clients[notified_socket]["data"].decode("utf-8")}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            msg = message["data"].decode("utf-8")
            if msg == "WinA" or msg == "WinB":
                winner = ""
                if msg == 'WinA':
                    winner = u1
                else:
                    winner = u2

                conn = pymysql.connect(host="localhost", user="root", passwd="", db="cn_python_db")
                myCursor = conn.cursor()
                query = "insert into game_stats (player1,player2,winner) values ("+u1+","+u2+","+winner+")"
                myCursor.execute(query)
                conn.commit()
                conn.close()

            for client in clients:
                if client != notified_socket:
                    client.send(user['header'] + user['data'] + message['header'] + message['data'])

        for not_soc in exception_sockets:
            sockets_list.remove(not_soc)
            del clients[not_soc]
