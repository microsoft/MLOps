import os
import json
import time
import iothub_client

from tracker import Tracker
from utils.parser import get_config
from settings.setting import get_setting_tracker
from iothub_client import (IoTHubModuleClient, IoTHubClientError, IoTHubError,
                           IoTHubMessage, IoTHubMessageDispositionResult,
                           IoTHubTransportProvider)

SEND_CALLBACKS = 0


def receive_message(message, hubManager):
    return IoTHubMessageDispositionResult.ACCEPTED


def send_to_Hub_callback(strMessage):
    print(strMessage)
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    hubManager.send_event_to_output("output", message, 0)


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1


class HubManager(object):

    def __init__(
            self,
            messageTimeout,
            protocol,
            verbose=False):

        self.messageTimeout = messageTimeout
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.client.set_option("messageTimeout", self.messageTimeout)
        self.client.set_option("product_info", "edge-engine-inference")
        if verbose:
            self.client.set_option("logtrace", 1)
        self.client.set_message_callback("output", receive_message, self)

    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)


def main():
    with Tracker() as trk:
        trk.run()

if __name__ == '__main__':
    main()
