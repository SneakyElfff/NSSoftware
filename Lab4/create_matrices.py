import numpy as np

M, N, K = 1024, 256, 512

def create_and_save_matrices():
    A = np.random.randint(100, size=(M, N))
    B = np.random.randint(100, size=(N, K))

    np.save('matrix_A.npy', A)
    np.save('matrix_B.npy', B)

    print("Матрицы A и B успешно созданы и сохранены в 'matrix_A.npy' и 'matrix_B.npy'.")

create_and_save_matrices()