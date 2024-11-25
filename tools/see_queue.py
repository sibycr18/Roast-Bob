from kafka import KafkaConsumer
import json
from datetime import datetime

def monitor_twitter_mentions(bootstrap_servers='localhost:9092', topic='twitter.mentions'):
    # Create consumer with different group ID
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='monitor_group',  # Different from 'twitter_roaster_group'
        auto_offset_reset='earliest',  # To see all messages
        enable_auto_commit=False  # Don't commit offsets to keep messages
    )
    
    print(f"Monitoring Kafka topic: {topic}")
    print("Waiting for messages... (Ctrl+C to exit)\n")
    
    try:
        for message in consumer:
            mention = message.value
            print("=" * 50)
            print(f"Timestamp: {datetime.fromtimestamp(message.timestamp/1000)}")
            print(f"Partition: {message.partition}")
            print(f"Offset: {message.offset}")
            print("\nMention Details:")
            print(f"Tweet ID: {mention.get('id')}")
            print(f"Text: {mention.get('text')}")
            print(f"Created At: {mention.get('created_at')}")
            print(f"Author ID: {mention.get('author_id')}")
            print(f"Referenced Tweet ID: {mention.get('referenced_tweet_id', 'N/A')}")
            print("=" * 50)
            print()
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        consumer.close()

if __name__ == "__main__":
    # You can modify these parameters based on your setup
    KAFKA_SERVERS = 'localhost:9092'  # Update if different
    KAFKA_TOPIC = 'twitter.mentions'
    
    monitor_twitter_mentions(KAFKA_SERVERS, KAFKA_TOPIC)