python3 create_matrices.py

docker-compose up -d --build 

docker exec -it mpi-node1 bash

mpirun --allow-run-as-root -np <num_of_procceses> python3 GroupAndFileOperations.py <num_of_group>
mpirun --allow-run-as-root -np 6 python3 GroupAndFileOperations.py 3