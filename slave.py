from xmlrpclib import ServerProxy

#Execute RPC
server = ServerProxy("http://localhost:8080")
print server.add(3,5)
print server.gen(2048)
