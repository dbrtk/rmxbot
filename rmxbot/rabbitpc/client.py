"""Client for the RabbitMQ rpc."""
import json
import pika
import uuid

from .. import config


CREDS = pika.PlainCredentials(config.RPC_USER, config.RPC_PASS)
CONNECTION_PARAMS = pika.ConnectionParameters(
    config.RPC_HOST, config.RPC_PORT, config.RPC_VHOST, CREDS)


class RpcConn(object):
    """RPC connection. This implements a pika.BlockingConnection. 
       It's because the client waits for the server's response. 
    """

    def __init__(self):

        self.connection = pika.BlockingConnection(parameters=CONNECTION_PARAMS)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = uuid.uuid4().hex
        
    def on_response(self, ch, method, props, body):
        """executed on response"""
        if self.corr_id == props.correlation_id:
            self.response = body

    def __call__(self, n: (dict, str, int, list,) = None):
    
        raise NotImplementedError()


class CallRmxgrep(RpcConn):
    """This class calls the rmxgrep endpoint to get a context for the selected
       feature.
    """
    
    def __init__(self):
        
        self.queue = config.RPC_PUBLISH_QUEUES.get('rmxgrep')
        super().__init__()

    def __call__(self, obj: dict = None):
        """Calling the remote machine through rpc/rabbit."""
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(obj))

        while self.response is None:
            self.connection.process_data_events()

        raise ValueError(self.response)
        return json.loads(self.response)
