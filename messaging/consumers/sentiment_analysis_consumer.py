import json
from kafka import KafkaConsumer, KafkaProducer
from config.kafka_config import KAFKA_CONFIG

#Placeholders

from nlp.preprocessing import clean_text
from nlp.sentiment_model import SentimentModel

def main():

    #Initialisation du consumer
    consumer = KafkaConsumer(
        KAFKA_CONFIG["topics"]["raw_news"],
        bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer= lambda m :json.loads(m.decode('utf-8'))
    )

    #Initialmisation du producer

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
        value_serializer= lambda v : json.dumps(v).encode('utf-8'),
        **KAFKA_CONFIG["producer_config"]
    )

    #Charger le modèle NLP

    model =SentimentModel()

    print("✅ Sentiment Analysis Consumer is running...")

    for msg in consumer:

        try:
            article=msg.value
            print(f"🔍 Received article: {article['title']}")
            #Nettoyage texte
            cleaned_content=clean_text(article["content"])
            #Predire le score du sentiment
            score=model.predict_sentiment(cleaned_content)

            enriched_article={
                **article,
                "sentiment_score":float(score)
            }

            #Envoyer dans news_sentiment
            
            producer.send(KAFKA_CONFIG["topics"]["news_sentiment"],value=enriched_article)
            print(f"📤 Sent enriched article with score {score}")

            with open('/home/saadyaq/SE/Python/finsentbot/data/raw/news_sentiment.jsonl',"a") as f:
                f.write(json.dumps(enriched_article) +'\n')
        except Exception as e:
            print(f"⚠️ Error processing message: {e}")

if __name__ == "__main__":
    main()