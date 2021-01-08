build:
	docker-compose up --build -d

stop:
	docker stop $$(docker ps -a -q)

remove:
	docker rm $(docker ps -a -q) -f

purge:
	docker rmi $(docker images) -f