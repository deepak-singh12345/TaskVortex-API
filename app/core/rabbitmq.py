import aio_pika 

connection: aio_pika.RobustConnection | None = None 
channel: aio_pika.abc.AbstractChannel | None = None 

async def connect_rabbitmq():
    global connection, channel 
    
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )
    
    channel = await connection.channel()
    
    await channel.declare_queue(
        "task_queue",
        durable=True,
    )
    
async def close_rabbitmq():
    if connection:
        await connection.close() 