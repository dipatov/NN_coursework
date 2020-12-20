#pragma once
#include "Matrix.h"
#include <algorithm>

using namespace std;

struct TetrisNet {
    Matrix m1, m2, bias1, bias2;
    bool flag = false;
    int score = 0;

    TetrisNet(int input, int hidden, int output)
        : m1(input, hidden),
        m2(hidden, output),
        bias1(1, hidden),
        bias2(1, output)
    {
    }

    TetrisNet& operator=(const TetrisNet& right) {
        if (this == &right) {
            return *this;
        }
        m1 = right.m1;
        m2 = right.m2;
        bias1 = right.bias1;
        bias2 = right.bias2;
        flag = right.flag;
        score = right.score;
        return *this;
    }

    void randomize() {
        m1.randomize();
        m2.randomize();
        bias1.randomize();
        bias2.randomize();
    }

    void mutant(double p) {
        m1.mutant(p);
        m2.mutant(p);
    }

    const Matrix forward(Matrix& in) {
        Matrix temp = in.dot(m1);
        for (int i = 0; i < temp.columns(); ++i) {
            temp.matr[0][i] += bias1.matr[0][i];
        }
        temp = relu(temp);
        temp = temp.dot(m2);
        for (int i = 0; i < temp.columns(); ++i) {
            temp.matr[0][i] += bias2.matr[0][i];
        }
        return temp;
    }

    const Matrix relu(Matrix in) {
        Matrix out(in.rows(), in.columns());
        for (int i = 0; i < in.rows(); ++i) {
            for (int j = 0; j < in.columns(); ++j) {
                out.matr[i][j] = max(0., in.matr[i][j]);
            }
        }
        return out;
    }

    bool operator< (const TetrisNet& a) const {
        return score < a.score;
    }
};
