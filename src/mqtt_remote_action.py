#!/usr/bin/env python3
""" MQTT test client for receiving rtl_433 JSON data

Example program for receiving and parsing sensor data from rtl_433 sent
as MQTT network messages. Recommended way of sending rtl_433 data on network is:

$ rtl_433 -F json -M utc | mosquitto_pub -t home/rtl_433 -l

An MQTT broker e.g. 'mosquitto' must be running on local computer

Copyright (C) 2017 Tommy Vestermark
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import datetime
import json
import logging
import multiprocessing as mp
import sys
import time

import paho.mqtt.client as mqtt
from picamera import PiCamera


MQTT_SERVER = "127.0.0.1"
MQTT_TOPIC_PREFIX = "home/rtl_433"
TIMEOUT_STALE_SENSOR = 600  # Seconds before showing a timeout indicator

# log = logging.getLogger()  # Single process logger
log = mp.log_to_stderr()  # Multiprocessing capable logger
mqtt_client = mqtt.Client("RTL_433_Test")
camera = PiCamera()


def take_image(ts):
    camera.capture('./imageshot_' + ts + '.jpg')





def on_connect(client, userdata, flags, rc):
    """ Callback for when the client receives a CONNACK response from the server. """
    log.info("MQTT Connection: " + mqtt.connack_string(rc))
    if rc != 0:
        log.error("Could not connect. RC: " + str(rc))
        exit()
    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_PREFIX)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        log.error("Unexpected disconnection. RC: " + str(rc))


def on_message(client, userdata, msg):
    """ Callback for when a PUBLISH message is received from the server. """
    if msg.topic.startswith(MQTT_TOPIC_PREFIX):
        try:
            # Decode JSON payload
            d = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            log.warning("JSON decode error: " + msg.payload.decode())
            return
        time_str = d.get('time', "0000-00-00 00:00:00")
        time_utc = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        take_image(time_str)
        
        
    else:
        log.info("Unknown topic: " + msg.topic + "\t" + msg.payload.decode())


# Setup MQTT client
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_SERVER)
mqtt_client.loop_start()


def main():
    """MQTT Test Client"""
    log.setLevel(logging.INFO)
    log.info("MQTT RTL_433 Test Client")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
