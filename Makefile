SHELL := /bin/bash

.PHONY: certs up down restart acls clean

certs:
	@echo "[certs] Generating CA and server/client certificates..."
	./scripts/generate-certs.sh

up: certs
	docker-compose up -d

restart: down up

down:
	docker compose down

# Example: make acls PRINCIPAL=customerA TOPIC=custA.*
acls:
	@if [ -z "$(PRINCIPAL)" ] || [ -z "$(TOPIC)" ]; then \
		echo "Usage: make acls PRINCIPAL=<user> TOPIC=<topic-pattern>"; exit 1; \
	fi
	docker exec kafka-broker kafka-acls --authorizer-properties zookeeper.connect=zookeeper:2181 \
	  --add --allow-principal User:$(PRINCIPAL) --producer --topic $(TOPIC)

clean:
	rm -rf security/certs 

run-allowed:
	python3 scripts/producer_allowed.py

run-denied:
	python3 scripts/producer_denied.py 

run-consumer-allowed:
	python3 scripts/consumer_allowed.py

run-consumer-denied:
	python3 scripts/consumer_denied.py 
