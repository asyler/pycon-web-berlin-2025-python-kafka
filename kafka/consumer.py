import random

from confluent_kafka import Consumer, KafkaError, TopicPartition

from kafka import KAFKA_TOPIC, NUM_OF_PARTITIONS


def read_messages_once(topic):
    return read_messages(topic, {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'read-once',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'false',
        'enable.partition.eof': True,
    })

def read_messages_live(topic, stop_event, sid):
    return read_messages(topic, config={
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'read-live-' + sid,
    }, stop_event=stop_event)

def read_messages_new(topic, partition=None):
    return read_messages(topic, {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'read-new' + ('-partitioned' if partition is not None else ''),
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'true',
        'enable.partition.eof': True,
    }, partition)

def read_messages_basic(topic):
    return read_messages(topic, config={
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'basic',
    })

def read_messages(topic, config, partition=None, stop_event=None):
    consumer = Consumer(config)
    if partition is None:
        consumer.subscribe([topic])
    else:
        partitions = [TopicPartition(topic, partition)]
        consumer.assign(partitions)

    print(f"Subscribed to topic: {topic}")
    partitions_read = 0
    try:
        while not stop_event or not stop_event.is_set():
            msg = consumer.poll(1.0)  # Poll for a message with a 1-second timeout

            if msg is None:
                # No message was received within the timeout
                continue
            if msg.error():
                # Handle errors
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
                    partitions_read += 1
                    if partition is not None or partitions_read == NUM_OF_PARTITIONS:
                        break
                else:
                    # Actual error
                    print(f"Kafka error: {msg.error()}")
                continue

            value = msg.value().decode('utf-8')
            print(f"Received message: {value}")
            yield value
        else:
            print('Stopped using stop event.')
    finally:
        # Ensure the consumer is properly closed
        consumer.close()
        print("Kafka consumer closed.")


if __name__ == '__main__':
    for msg in read_messages_basic(KAFKA_TOPIC):
        print(msg)
