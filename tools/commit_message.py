from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
import json

# Define the consumer
consumer = KafkaConsumer(
    'twitter.mentions',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='twitter_roaster_group',
    auto_offset_reset='latest',
    enable_auto_commit=False  # Disable auto commit
)

# Consume messages
for message in consumer:
    item = json.dumps(message.value, indent=2)
    print(f"Consumed message: {item}\n")
    # consumer.commit()

    # # Check for the desired condition
    # if message.value.get('id') == '1860861236134715764':
    #     print("Condition matched, committing this message.")

    #     # Get the TopicPartition for the current message
    #     topic_partition = TopicPartition(message.topic, message.partition)
        
    #     # Commit the specific offset for this message
    #     consumer.commit({
    #         topic_partition: OffsetAndMetadata(message.offset + 1, '')
    #     })
    #     break
