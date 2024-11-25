from kafka import KafkaProducer
import json
import time

def publish_mentions(bootstrap_servers='localhost:9092', topic='twitter.mentions'):
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Load mentions from JSON file
    with open('mentions-copy.json', 'r') as file:
        mentions = json.load(file)
    
    print(f"Publishing {len(mentions)} mentions to topic: {topic}")
    # exit()

    # Publish each mention
    for mention in mentions:
        try:
            # Send message
            future = producer.send(topic, value=mention)
            # Wait for message to be sent
            record_metadata = future.get(timeout=10)
            
            print(f"\nPublished mention:")
            print(f"Tweet ID: {mention['id']}")
            print(f"Text: {mention['text']}")
            print(f"Partition: {record_metadata.partition}")
            print(f"Offset: {record_metadata.offset}")
            print("-" * 50)
            
            # Small delay between messages
            time.sleep(1)
            
        except Exception as e:
            print(f"Error publishing mention {mention['id']}: {str(e)}")
    
    # Clean up
    producer.flush()
    producer.close()
    
    print("\nFinished publishing all mentions")

if __name__ == "__main__":
    # You can modify these parameters based on your setup
    KAFKA_SERVERS = 'localhost:9092'  # Update if different
    KAFKA_TOPIC = 'twitter.mentions'
    
    publish_mentions(KAFKA_SERVERS, KAFKA_TOPIC)