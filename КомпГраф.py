import numpy as np
import math # Импортируем модуль math

def determinant(matrix):
    """
    Рекурсивно вычисляет детерминант квадратной матрицы.
    """
    size = matrix.shape[0]

    if size == 1:
        return matrix[0, 0]
    
    det = 0

    for i in range(size):

        sub_matrix = np.delete(np.delete(matrix, 0, axis=0), i, axis=1)
        sign = (-1) ** i
        det += sign * matrix[0, i] * determinant(sub_matrix)

    return det

def simplex_volume(points):
    """
    Вычисляет n-мерный объем симплекса, заданного n+1 точками.
    """
    points = np.array(points)
    num_points, dim = points.shape

    if num_points != dim + 1:
        raise ValueError("Количество точек должно быть на 1 больше размерности пространства.")
    
    # Матрица векторов, идущих из первой точки в остальные
    vector_matrix = points[1:] - points[0]

    det = determinant(vector_matrix)

    # Объем = (1/n!) * |det|
    volume = abs(det) / math.factorial(dim)
    
    return volume

# --- Тестовый блок ---
if __name__ == "__main__":
    print("Запускаю тесты...")

    # Тест 1: Площадь стандартного треугольника
    points_2d = [[0, 0], [2, 0], [1, 2]]
    expected_area = 2.0
    # math.isclose используется для корректного сравнения чисел с плавающей точкой
    assert math.isclose(simplex_volume(points_2d), expected_area), f"Ошибка в тесте для 2D треугольника"

    # Тест 2: Объем стандартного тетраэдра
    points_3d = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    expected_volume = 1/6
    assert math.isclose(simplex_volume(points_3d), expected_volume), f"Ошибка в тесте для 3D тетраэдра"

    # Тест 3: Длина отрезка (1D симплекс)
    points_1d = [[1], [5]]
    expected_length = 4.0
    assert math.isclose(simplex_volume(points_1d), expected_length), f"Ошибка в тесте для 1D отрезка"
    
    # Тест 4: Вырожденный случай (точки на одной прямой, площадь равна 0)
    points_degenerate = [[0, 0], [1, 1], [3, 3]]
    expected_degenerate = 0.0
    assert math.isclose(simplex_volume(points_degenerate), expected_degenerate), f"Ошибка в тесте на вырожденный случай"

    # Тест 5: Проверка вызова ошибки при неверном количестве точек
    try:
        invalid_points = [[0, 0], [1, 0], [0, 1], [1, 1]] # 4 точки в 2D
        simplex_volume(invalid_points)
        # Если код дошел сюда, значит ошибка НЕ была вызвана, и тест провален
        assert False, "Тест на исключение провален: ValueError не был вызван"
    except ValueError:
        # Ошибка была успешно перехвачена, значит тест пройден
        pass 
    
    print("Все тесты успешно пройдены! ✅")