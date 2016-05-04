#!/bin/sh

filename="$1"
while read -r line
do
    name=$line
    scp -r /root/Morph root@$name:/root/
    #scp get_host_name.py root@$name:/tmp/
done < "$filename"
