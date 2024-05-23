#!/usr/bin/env python3

"""TLS-Enabled Chat Server for CST311 Programming Assignment 4"""
__author__ = "Divine Web Design"
__credits__ = [
    "Mike Divine",
    "Russell Frost",
    "Kenneth Ao",
    "Ben Shafer"
]

# Multithreading is needed so the client and server can operate concurrently,
# allowing for simultaneous communication between the clients and the server.
# Each client and server thread can execute independently, ensuring that
# multiple clients can connect and send messages simultaneously.

# Import threading to use multithreading so the server can handle multiple
# TCP clients simultaneously. Each client connection will have its own thread
# otherwise the server will be blocked, and it won't be able to accept new
# client connection requests until the current one is completed.
import socket as s
import threading
import ssl

# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Global variables
server_name = 'chatserver.cst311.test'
server_port = 12000
connection_count = 0
message_count = 0
message = None
event = threading.Event()  # Event used to synchronize client connection threads.
certfile = f'/etc/ssl/demoCA/newcerts/{server_name}-cert.pem'
keyfile = f'/etc/ssl/demoCA/private/{server_name}-key.pem'

#Context is the TLS protocol.
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile, keyfile)


def connection_handler(connection_socket, address):
  # global variables declared, so they can be updated outside the local scope
  # and shared between threads.
  global connection_count
  global message_count
  global message

  # First client to connect is X and second is Y
  connection_count += 1
  if connection_count % 2 == 1:
    client = "X"
  else:
    client = "Y"

  secure_connection_socket = context.wrap_socket(connection_socket, server_side=True)
  # Read data from the new connection socket
  # Note: if no data has been sent this blocks until there is data
  query = secure_connection_socket.recv(1024)

  # Decode data from UTF-8 bytestream
  query_decoded = query.decode()
  
  # Log query information
  log.info("Received query test \"" + str(query_decoded) + "\"")

  # Perform some server operations on data to generate response
  response = query_decoded.upper()

  # The thread of the first client message received waits until the second
  # message is received. Once the second message is received, both threads
  # proceed.The messages are concatenated in the order they are received.
  message_count += 1
  if message_count % 2 == 0:
    message = (message + ", " + client + ": " + response)
    event.set()
  if message_count % 2 == 1:
    message = (client + ": " + response)
    event.wait()

  # Send both messages received over the network, encoding to UTF-8
  secure_connection_socket.send(message.encode())
  
  # Close client socket
  secure_connection_socket.close()

  # The event used to pause the threads is reset to allow 2 new client connections.
  event.clear()


def main():
  # Create a TCP socket
  # Notice the use of SOCK_STREAM for TCP packets
  server_socket = s.socket(s.AF_INET,s.SOCK_STREAM)
  
  # Assign IP address and port number to socket, and bind to chosen port
  server_socket.bind(('',server_port))
  
  # Configure how many requests can be queued on the server at once
  server_socket.listen(1)
  
  # Alert user we are now online
  log.info("The server is ready to receive on port " + str(server_port))
  
  # Surround with a try-finally to ensure we clean up the socket after we're done
  try:
    # Enter forever loop to listen for requests
    while True:
      # When a client connects, create a new socket and record their address
      connection_socket, address = server_socket.accept()
      log.info("Connected to client at " + str(address))
      # Pass the new socket and address off to a connection handler function.
      # The connection handler is started in its own thread so the server can
      # continue to accept new client connections.
      threading.Thread(target=connection_handler, args=(connection_socket, address)).start()
  finally:
    server_socket.close()


if __name__ == "__main__":
  main()