docker-compose up -d --build 

docker exec mpi-node1 ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa

docker exec mpi-node1 cat /root/.ssh/id_rsa.pub > temp_key

docker exec mpi-node2 mkdir -p /root/.ssh
docker exec -i mpi-node2 tee -a /root/.ssh/authorized_keys < temp_key
docker exec mpi-node3 mkdir -p /root/.ssh
docker exec -i mpi-node3 tee -a /root/.ssh/authorized_keys < temp_key

rm temp_key

docker exec -it mpi-node1 ssh root@192.168.1.102 hostname

docker exec -it mpi-node1 mpirun --allow-run-as-root -np 3 --host 192.168.1.101,192.168.1.102,192.168.1.103 python3 MatrixMul.py