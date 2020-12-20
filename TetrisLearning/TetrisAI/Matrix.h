#pragma once
#include <vector>
#include <random>

using namespace std;

struct Matrix {
    vector<vector<double>> matr;


    Matrix() = default;

    Matrix(int rows, int columns)
        : matr(rows, vector<double>(columns))
    {
    }

    const Matrix dot(const Matrix& r) {
        Matrix result(matr.size(), r.matr[0].size());
        for (int i = 0; i < matr.size(); ++i) {
            for (int j = 0; j < r.matr[0].size(); ++j) {
                double sum = 0;
                for (int k = 0; k < matr[0].size(); ++k) {
                    sum += matr[i][k] * r.matr[k][j];
                }
                result.matr[i][j] = sum;
            }
        }
        return result;
    }

    void randomize() {
        random_device randomDevice;
        mt19937 randomGen(randomDevice());
        uniform_real_distribution<double> distribution(-1, 1);
        for (int i = 0; i < matr.size(); ++i) {
            for (int j = 0; j < matr[0].size(); ++j) {
                matr[i][j] = distribution(randomGen);
            }
        }
    }

    void mutant(double p) {
        random_device randomDevice;
        mt19937 randomGen(randomDevice());
        normal_distribution<double> norm(0, 1);
        bernoulli_distribution b(p);
        for (int i = 0; i < rows(); ++i) {
            for (int j = 0; j < columns(); ++j) {
                if (b(randomGen)) {
                    matr[i][j] = norm(randomGen);
                }
            }
        }
    }

    const int rows() {
        return matr.size();
    }

    const int columns() {
        return matr[0].size();
    }

    Matrix& operator= (const Matrix& r)
    {
        matr = r.matr;
        return *this;
    }
};


