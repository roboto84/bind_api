# Socket Client Network base class

import os
import ast
from typing import List, Any, NoReturn
from socket import AF_INET, socket, SOCK_STREAM


class ClientNetwork:
    BUFFER_SIZE: int = 1024
    message_history: List[dict] = []

    def __init__(self, logging_object: Any, host: str, port: int) -> NoReturn:
        self.logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging_object.INFO)

        self.number_of_messages = 0
        self.client_socket = None
        self.client_socket_error = False
        self.close_app = None
        self.address = (host, port)

    def sock_it(self) -> NoReturn:
        try:
            self.logger.info(f'Attempting socket connection to {self.address}')
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.address)
            self.logger.info(f'Connection to {self.address} has succeeded')
        except ConnectionRefusedError as connection_refused_error:
            self.logger.error(f'Received ConnectionRefusedError: {(str(connection_refused_error))}')
            os._exit(1)
        except OSError as os_error:  # Possibly client has left the chat.
            self.logger.error(f'Received an OSError: {(str(os_error))}')
            os._exit(1)

    def send_message(self, message) -> NoReturn:
        if self.client_socket_error:
            os._exit(1)
        else:
            try:
                self.client_socket.send(bytes(message, 'utf8'))
            except IOError as io_error:
                self.logger.error(f'Received IOError: {(str(io_error))}')
                self.client_socket_error = True

    def receive(self) -> NoReturn:
        while True:
            try:
                message = self.client_socket.recv(self.BUFFER_SIZE)
                package: dict = ast.literal_eval(message.decode('utf8', errors='replace'))
                if package['id'] != 'wh00t_server' and package['profile'] != 'user':
                    self.number_of_messages += 1
                    self.message_history.append(package)
                    print(f'received message: {str(package)}')
            except OSError as os_error:  # Possibly client has left the chat.
                self.logger.error(f'Received OSError: {(str(os_error))}')
                break
            except KeyboardInterrupt:
                self.logger.warning('Received a KeyboardInterrupt... now exiting')
                self.client_socket.close()
                os._exit(1)

    def get_message_history(self) -> List[dict]:
        self.trim_message_history()
        return self.message_history

    def trim_message_history(self) -> NoReturn:
        if len(self.message_history) > 20:
            self.message_history.pop(0)
