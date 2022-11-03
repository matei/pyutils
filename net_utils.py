import socket


def get_next_open_port(port_start):
    """
    Get first open port starting with port_start
    :param port_start:
    :return:
    """
    while is_port_open(port_start):
        port_start += 1
    return port_start


def is_port_open(port):
    """
    Check if port is open on local
    :param port:
    :return:
    """
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = ("127.0.0.1", port)
    result_of_check = a_socket.connect_ex(location)

    return result_of_check == 0
