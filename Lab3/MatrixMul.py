from mpi4py import MPI
import numpy as np

def blockMode(A, B, M, N, K):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    rows_per_process = M // size
    extra_rows = M % size

    if rank < extra_rows:
        local_rows = rows_per_process + 1
    else:
        local_rows = rows_per_process

    if rank == 0:
        block_A = [A[i * rows_per_process + min(i, extra_rows):(i + 1) * rows_per_process + min(i + 1, extra_rows), :]
                   for i in range(size)]
    else:
        block_A = None

    sub_A = comm.scatter(block_A, root=0)

    comm.Bcast(B, root=0)

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
        print(f"Elapsed time for blocking matrix multiplication: {elapsed_time:.6f} seconds")
        return C, elapsed_time
    return None, None


def notBlockMode(A, B, M, N, K):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    rows_per_process = M // size
    extra_rows = M % size

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
        return C, elapsed_time
    return None, None


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # Матрицы генерируются один раз на процессе 0
    M, N, K = 1024, 256, 512
    if rank == 0:
        A = np.random.randint(100, size=(M, N))
        B = np.random.randint(100, size=(N, K))
    else:
        A = None
        B = None

    # Распространяем матрицы A и B на все процессы
    A = comm.bcast(A, root=0)
    B = comm.bcast(B, root=0)

    if rank == 0:
        print("Starting matrix multiplication in blocking mode...")
    C_block, time_block = blockMode(A, B, M, N, K)

    comm.Barrier()

    if rank == 0:
        print("Switching to non-blocking mode...")
    C_nonblock, time_nonblock = notBlockMode(A, B, M, N, K)

    if rank == 0:
        print("Comparing results...")
        if np.array_equal(C_block, C_nonblock):
            print("Results match!")
        else:
            print("Results do NOT match!")

        print(f"Blocking mode time: {time_block:.6f} seconds")
        print(f"Non-blocking mode time: {time_nonblock:.6f} seconds")


if __name__ == "__main__":
    main()
    MPI.Finalize()
