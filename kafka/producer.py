from confluent_kafka import Producer

from kafka import KAFKA_TOPIC

config = {
    'bootstrap.servers': 'localhost:9092',
}

producer = Producer(config)

def delivery_report(err, msg):
    if err:
        print(f"Message failed delivery: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def send_message(topic, message, partition=None):
    try:
        producer.produce(topic, message.encode('utf-8'), partition=partition, callback=delivery_report)
        producer.flush()  # Ensure all messages are sent
    except Exception as e:
        print(f"Error producing message: {e}")

if __name__ == '__main__':
    send_message(KAFKA_TOPIC, "Hello World")
