# MQStackYWH


### 1. Start RabbitMQ, InfluxDB and Grafana
```bash
docker compose up -d broker tsdb frontend
```

### 2. Start workers
```bash
docker compose up worker
```

### 3. Run crawler
```bash
docker compose run crawler
```

### 4. Results on grafana
http://localhost:3000
> *login:* admin\
> *password:* admin1234
