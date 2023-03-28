# Spawn data infrastructure
```bash
make up

# checking redpanda console
make to_redpanda

# checking minio
make to_minio
```

# Prepare MySQL data source
```bash
make to_mysql

CREATE DATABASE brazillian_ecommerce;

USE brazillian_ecommerce;

CREATE TABLE olist_orders_dataset (
    order_id varchar(32),
    customer_id varchar(32),
    order_status varchar(16),
    order_purchase_timestamp varchar(32),
    order_approved_at varchar(32),
    order_delivered_carrier_date varchar(32),
    order_delivered_customer_date varchar(32),
    order_estimated_delivery_date varchar(32),
    PRIMARY KEY (order_id)
);

```

# Generation scripts
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/01_generate_orders.py
```

# CDC to Redpanda
```bash
# health check Kafka connect
curl -H "Accept:application/json" localhost:8083/connector-plugins/
curl -H "Accept:application/json" localhost:8083/connectors/

# create src-brazillian-ecommerce connector
curl --request POST \
  --url http://localhost:8083/connectors \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "src-brazillian-ecommerce",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.id": "184054",
    "database.include.list": "brazillian_ecommerce",
    "topic.prefix": "dbserver1",
    "schema.history.internal.kafka.bootstrap.servers": "redpanda:9092",
    "schema.history.internal.kafka.topic": "schema-changes.brazillian_ecommerce"
  }
}'
```

# Redpanda to MinIO
```bash
# download Amazon S3 Sink Connector
wget https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.3.1/confluentinc-kafka-connect-s3-10.3.1.zip

# copy connectors to kafka/connect
unzip confluentinc-kafka-connect-s3-10.3.1.zip
docker cp confluentinc-kafka-connect-s3-10.3.1 kafka_connect:/kafka/connect

# restart kafka_connect to reload list plugins
docker restart kafka_connect
    
# create connector S3
curl --request POST \
  --url http://localhost:8083/connectors \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "sink-s3-brazillian-ecommerce",  
  "config": {
    "topics.regex": "dbserver1.brazillian_ecommerce.*",
    "topics.dir": "brazillian_ecommerce",
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "100",
    "store.url": "http://minio:9000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "s3.region": "us-east-1",
    "s3.bucket.name": "warehouse",    
    "aws.access.key.id": "minio",
    "aws.secret.access.key": "minio123"
  }
}'
```

# Clickstream to MinIO
```bash
# create connector sink clickstream to S3
curl --request POST \
  --url http://localhost:8083/connectors \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "sink-s3-clickstream",
  "config": {
    "topics": "clickstream_events",
    "topics.dir": "clickstream_events",
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "key.converter.schemas.enable": "false",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "s3.compression.type": "gzip",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "100",
    "store.url": "http://minio:9000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "s3.region": "us-east-1",
    "s3.bucket.name": "warehouse",
    "aws.access.key.id": "minio",
    "aws.secret.access.key": "minio123"
  }
}'
```

# Wrapup setup connectors
```bash
cd src/
chmod +x setup_connectors.sh
./setup_connectors.sh
```