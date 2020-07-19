.PHONY: clean test preapre-local-dev-environment

test:
	bats tests/
clean:
	docker-compose kill
	docker-compose rm -f
	docker-compose down

preapre-local-dev-environment:
	sudo apt-get update && sudo apt-get -y install bats
	cd dockerfiles/apache && make
	cd dockerfiles/haproxy && make
