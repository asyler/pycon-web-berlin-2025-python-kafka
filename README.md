# Data in Motion: Python-Powered Kafka Pipelines

Welcome to the repository for the talk **"Data in Motion: Python-Powered Kafka Pipelines"**, presented at [PyCon+Web 2025](https://www.pyconweb.com/activity/scalable-kafka-data-pipeline). This repository contains all the code and resources used during the talk.

## Quick Start

1. Start the Kafka ecosystem:

    ```bash
    docker-compose up -d
    ```

2. Run the producer to send messages to Kafka:

    ```bash
    python kakfa/producer.py
    ```

3. Start the consumer to process the messages:

    ```bash
    python kafka/consumer.py
    ```

4. Run Flask server with the demo pages:

    ```bash
    python flask/server.py
    ```

## Links
- [Presentation at PyCon+Web](https://www.pyconweb.com/activity/scalable-kafka-data-pipeline)
- [Connect on LinkedIn](https://www.linkedin.com/in/vladyslav-krasnolutskyi/)
- [KIP-932: Queues for Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka)

## License
This project is licensed under the MIT License. See the LICENSE file for details.
