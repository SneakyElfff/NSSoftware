[//]: # (python3 generate.py <matrix_size>)

docker-compose up -d --build 

docker exec -it mpi-node1 bash

mpirun --allow-run-as-root -np <count_of_procceses> python3 GroupAndFileOperations.py <count_of_group>