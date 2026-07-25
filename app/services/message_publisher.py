import json

from aio_pika import Message, DeliveryMode

from app.core import rabbitmq

async def publish_message(message: dict) -> None:
    if rabbitmq.channel is None:
        raise RuntimeError("RabbitMQ channel is not initialized")
    
    await rabbitmq.channel.default_exchange.publish(
        Message(
            body=json.dumps(message).encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        ),
        routing_key="task_queue",
    )