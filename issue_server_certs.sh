#!/usr/bin/env bash

# Set the Root CA passphrase to the one you created in Lab 6a.
RootCA_passphrase=mininet

# Prompt user for the Common Name to the Web server and the chat server.
echo Enter the Common Name \(CN\) for the simple Web server:
read web_server_name
echo Enter the Common Name \(CN\) for the chat server:
read chat_server_name

# Set working directory to the demoCA created in Lab 6a.
cd /etc/ssl/demoCA

# Generate private key for Web server.
sudo openssl genrsa -out $web_server_name-key.pem 2048

# Generate certificate signing request for Web server.
sudo openssl req -nodes -new -config /etc/ssl/openssl.cnf \
			-key $web_server_name-key.pem \
			-out $web_server_name.csr \
			-subj "/C=US/ST=CA/L=Seaside/O=CST311/OU=Networking/CN=$web_server_name"

# Use Root CA to create the X.509 Web server certificate.
sudo openssl x509 -req -days 365 -in $web_server_name.csr \
			-CA cacert.pem \
			-CAkey /etc/ssl/demoCA/private/cakey.pem \
			-CAcreateserial \
			-out $web_server_name-cert.pem \
			-passin pass:$RootCA_passphrase

# Move the Web server key and certificate to the appropriate folders.
sudo mv $web_server_name-cert.pem /etc/ssl/demoCA/newcerts
sudo mv $web_server_name-key.pem /etc/ssl/demoCA/private


# generate private key for chat server
sudo openssl genrsa -out $chat_server_name-key.pem 2048

# generate certificate signing request for chat server
sudo openssl req -nodes -new -config /etc/ssl/openssl.cnf \
			-key $chat_server_name-key.pem \
			-out $chat_server_name.csr \
			-subj "/C=US/ST=CA/L=Seaside/O=CST311/OU=Networking/CN=$chat_server_name"

# Use Root CA to create the X.509 chat server certificate.
sudo openssl x509 -req -days 365 -in $chat_server_name.csr \
			-CA cacert.pem \
			-CAkey /etc/ssl/demoCA/private/cakey.pem \
			-CAcreateserial \
			-out $chat_server_name-cert.pem \
			-passin pass:$RootCA_passphrase

# Move the chat server key and certificate to the appropriate folders.
sudo mv $chat_server_name-cert.pem /etc/ssl/demoCA/newcerts
sudo mv $chat_server_name-key.pem /etc/ssl/demoCA/private