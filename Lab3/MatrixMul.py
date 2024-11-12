from mpi4py import MPI
import numpy as np


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    M = 1024
    N = 256
    K = 512

    if rank == 0:
        A = np.random.randint(100, size=(M, N))
        B = np.random.randint(100, size=(N, K))
    else:
        A = None
        B = np.empty((N, K), dtype=int)

    comm.Bcast(B, root=0)

    rows_per_process = M // size
    extra_rows = M % size

    if rank < extra_rows:
        local_rows = rows_per_process + 1
    else:
        local_rows = rows_per_process

    if rank == 0:
        block_A = [A[i * local_rows + min(i, extra_rows):i * local_rows + min(i, extra_rows) + local_rows, :]
                   for i in range(size)]
    else:
        block_A = None

    sub_A = comm.scatter(block_A, root=0)

    comm.Barrier()  # синхронизировать перед замером
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
        print("Elapsed time for blocking matrix multiplication: {:.6f} seconds".format(elapsed_time))

        # print("Matrix A:")
        # print(A)
        # print("Matrix B:")
        # print(B)
        # print("Matrix C (Result):")
        # print(C)


if __name__ == "__main__":
    main()
    MPI.Finalize()
