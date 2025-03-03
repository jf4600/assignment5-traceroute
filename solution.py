import socket
from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.

    myChecksum = 0
    packID = os.getpid() & 0xffff
    icmpHead = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, packID, 1)
    dataTime = struct.pack("d", time.time())
    myChecksum = checksum(icmpHead + dataTime)
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end

    # So the function ending should look like this
    icmpHead = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, packID, 1)
    packet = icmpHead + dataTime
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces
    destAddr = gethostbyname(hostname)

    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):

            #Fill in start
            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    #Fill in end
                recPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist2.append(tracelist1)
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                header = recPacket[20:28]
                types, code, checksum, packID, sequence = struct.unpack("bbHHh", header)
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    tracelist1.append(gethostbyaddr(str(addr[0]))[0])
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    tracelist1.append("hostname not found")
                    #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recPacket[28:28 + bytes])[0]
                    #Fill in start
                    tracelist1.insert(-1, str(int((timeReceived - t) * 1000)) + "ms")
                    tracelist1.insert(-1, addr[0])
                    tracelist2.append(tracelist1)
                    #You should add your responses to your lists here
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recPacket[28:28 + bytes])[0]
                    #Fill in start
                    tracelist1.insert(-1, str(int((timeReceived - t) * 1000)) + "ms")
                    tracelist1.insert(-1, addr[0])
                    tracelist2.append(tracelist1)
                    #You should add your responses to your lists here
                    #Fill in end
                elif types == 0:
                    #tracelist1 = [str(ttl), str((timeReceived - timeSent) * 1000) + "ms", addr[0], host]
                    #everywhere you have tracelist1.append   - change to tracelist1 = [....]  and then do a tracelist2.append(tracelist1)
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recPacket[28:28 + bytes])[0]
                    #Fill in start
                    tracelist1.insert(-1, str(int((timeReceived - t) * 1000)) + "ms")
                    tracelist1.insert(-1, addr[0])
                    tracelist2.append(tracelist1)
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    print(tracelist2)
                    #should look like
                    #[[str(ttl), str(delaytime), ip, hostname], ["Timeout Recieved"],[str(ttl), str(delaytime), ip, hostname].....]
                    return tracelist2
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist2.append(tracelist1)
                    #Fill in end
                break
            finally:
                mySocket.close()


if __name__ == '__main__':
    get_route("google.co.il")