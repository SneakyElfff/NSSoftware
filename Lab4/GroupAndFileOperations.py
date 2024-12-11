from mpi4py import MPI
import sys
import numpy as np

def groupMode(group_comm, group, rank, group_ranks):
    if group_comm == MPI.COMM_NULL:
        return

    A_file = "matrix_A.npy"
    B_file = "matrix_B.npy"
    C_file = f"matrix_C_group_{group}.npy"

    A = np.load(A_file, mmap_mode='r')
    B = np.load(B_file)

    rows_per_process = A.shape[0] // len(group_ranks)
    extra_rows = A.shape[0] % len(group_ranks)

    if rank == group_ranks[0]:
        block_A = [A[i * rows_per_process + min(i, extra_rows):(i + 1) * rows_per_process + min(i + 1, extra_rows), :]
                   for i in range(len(group_ranks))]
    else:
      block_A = None

    sub_A = group_comm.scatter(block_A, root=0)
    group_comm.Bcast(B, root=0)

    start_group_time = MPI.Wtime()

    sub_C = np.zeros((sub_A.shape[0], B.shape[1]), dtype=int)
    for i in range(sub_A.shape[0]):
      for j in range(B.shape[1]):
        for k in range(B.shape[0]):
          sub_C[i, j] += sub_A[i, k] * B[k, j]

    if rank == group_ranks[0]:
        end_group_time = MPI.Wtime()

    C_gathered = group_comm.gather(sub_C, root=0)

    if group_comm.Get_rank() == 0:
        C = np.vstack(C_gathered)
        elapsed_group_time = end_group_time - start_group_time
        np.save(C_file, C)
        print(
            f"Group {group}: Elapsed time for blocking matrix multiplication: {elapsed_group_time:.3f} seconds\nGroup {group}: Result saved to {C_file}")
        return C, elapsed_group_time
    return None, None

def notBlockMode(comm, rank, size, M, N, K):
  rows_per_process = M // size
  extra_rows = M % size
  if rank == 0:
    A = np.load('matrix_A.npy', mmap_mode='r')

    if rank == 0:
      block_A = [A[i * rows_per_process + min(i, extra_rows):(i + 1) * rows_per_process + min(i + 1, extra_rows), :]
                  for i in range(size)]
    else:
      block_A = None

  local_rows = rows_per_process + 1 if rank < extra_rows else rows_per_process
  sub_A = np.empty((local_rows, N), dtype=int)

  if rank == 0:
    requests = []
    for i in range(size):
      if i == rank:
        sub_A[:] = block_A[i]
      else:
        req = comm.Isend(block_A[i], dest=i, tag=100 + i)
        requests.append(req)
    MPI.Request.Waitall(requests)
  else:
    comm.Irecv(sub_A, source=0, tag=100 + rank).Wait()

  B = np.load('matrix_B.npy')
  request_b = comm.Ibcast(B, root=0)
  request_b.Wait()

  comm.Barrier()
  start_time = MPI.Wtime()

  sub_C = np.zeros((sub_A.shape[0], K), dtype=int)
  for i in range(sub_A.shape[0]):
    for j in range(K):
      for k in range(N):
        sub_C[i, j] += sub_A[i, k] * B[k, j]

  comm.Barrier()
  end_time = MPI.Wtime()

  C_gathered = comm.gather(sub_C, root=0)

  if rank == 0:
    C = np.vstack(C_gathered)

    elapsed_time = end_time - start_time
    print(f"Elapsed time for non-blocking matrix multiplication: {elapsed_time:.6f} seconds")
    np.save('pairwise_output.npy', C)
    return C, elapsed_time
  return None, None

def main():
  comm = MPI.COMM_WORLD
  size = comm.Get_size()
  rank = comm.Get_rank()

  M, N, K = 1024, 256, 512

  if len(sys.argv) < 2:
    if rank == 0:
      print("Usage: mpirun -np <total_processes> python program.py <num_groups>")
    exit()

  num_groups = int(sys.argv[1])

  if rank == 0:
    group_assignments = [np.random.randint(0, num_groups) for _ in range(size)]
  else:
    group_assignments = None

  group_assignments = comm.bcast(group_assignments, root=0)
  group = group_assignments[rank]

  group_ranks = [i for i in range(size) if group_assignments[i] == group]
  group = MPI.Group.Incl(comm.Get_group(), group_ranks)
  group_comm = comm.Create(group)

  if group_comm != MPI.COMM_NULL:
    print(f"Process {rank} is in group {group} with ranks {group_ranks}")

    groupMode(group_comm, group, rank, group_ranks)
    group_comm.Free()
  group.Free()
  # A = np.load('matrixA.npy', mmap_mode='r')
  notBlockMode(comm, rank, size, M, N, K)

if __name__ == "__main__":
    main()
