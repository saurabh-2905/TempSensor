from network import LoRa
import socket
import time
import ubinascii
import json

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915

def connectToTTN(): 
    lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)

    # # create an OTAA authentication parameters, change them to the provided credentials
    # app_eui = ubinascii.unhexlify('0000000000000000')
    # app_key = ubinascii.unhexlify('21FB06131C0CEF7B46ABCE61FB14E296')
    # #uncomment to use LoRaWAN application provided dev_eui
    # dev_eui = ubinascii.unhexlify('70B3D57ED0056D92')

    # join a network using OTAA (Over the Air Activation)
    #uncomment below to use LoRaWAN application provided dev_eui
    #lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    # lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    i=0
    while i<5:
        time.sleep(2.5)
        print('Not yet joined TTN...')
        i += 1

    print('Joined TTN!')


def sendSocketData(data):
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(False)

    # send some data
    s.send(data)

    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.close()