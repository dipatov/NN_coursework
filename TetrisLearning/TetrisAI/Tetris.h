#pragma once
#include <vector>
#include <iostream>
#include <random>
#include <algorithm>
#include "TetrisNet.h"
#include "Matrix.h"

using namespace std;

struct Tetris {
    vector<vector<int>> field;
    int score = 0;
    const vector<vector<vector<int>>> I = {
        {
            {1,1,1,1}
        },
        {
            {1},
            {1},
            {1},
            {1}
        }
    };
    const vector<vector<vector<int>>> T = {
        {
            {0,1,0},
            {1,1,1}
        },
        {
            {1,1,1},
            {0,1,0}
        },
        {
            {1,0},
            {1,1},
            {1,0}
        },
        {
            {0,1},
            {1,1},
            {0,1}
        }
    };
    const vector<vector<vector<int>>> S = {
        {
            {0,1,1},
            {1,1,0}
        },
        {
            {1,0},
            {1,1},
            {0,1}
        }
    };
    const vector<vector<vector<int>>> Z = {
        {
            {1,1,0},
            {0,1,1}
        },
        {
            {0,1},
            {1,1},
            {1,0}
        }
    };
    const vector<vector<vector<int>>> O = {
        {
            {1,1},
            {1,1}
        }
    };
    const vector<vector<vector<int>>> J = {
        {
            {1,0,0},
            {1,1,1}
        },
        {
            {1,1},
            {1,0},
            {1,0}
        },
        {
            {1,1,1},
            {0,0,1}
        },
        {
            {0,1},
            {0,1},
            {1,1}
        }
    };
    const vector<vector<vector<int>>> L = {
        {
            {0,0,1},
            {1,1,1}
        },
        {
            {1,0},
            {1,0},
            {1,1}
        },
        {
            {1,1,1},
            {1,0,0}
        },
        {
            {1,1},
            {0,1},
            {0,1}
        }
    };

    const vector< vector<vector<vector<int>>>> shape = { S, Z, I, O, J, L, T };

    vector<vector<vector<int>>> current_shape;

    Tetris()
        : field(20, vector<int>(10))
    {}

    void delete_lines() {
        for (int i = 0; i < 20; ++i) {
            bool flag = true;
            for (int j = 0; j < 10; ++j) {
                if (field[i][j] == 0) {
                    flag = false;
                    break;
                }
            }
            if (flag) {
                score++;
                for (int k = i - 1; k >= 0; k--) {
                    field[k + 1] = field[k];
                }
                field[0].assign(10, 0);
            }
        }
    }

    void new_shape() {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> distrib(0, 6);
        current_shape = shape[distrib(gen)];
    }

    bool put_at(vector<vector<int>>& field, int x, int y, int rot) {
        if (y < 0) {
            return false;
        }
        for (int i = y; i < y + current_shape[rot].size(); ++i) {
            for (int j = x; j < x + current_shape[rot][0].size(); ++j) {
                if (current_shape[rot][i - y][j - x] == 1) {
                    field[i][j] = current_shape[rot][i - y][j - x];
                }
            }
        }
        return true;
    }

    bool get_field_with_fig(vector<vector<int>>& field, int rot, int i) {
        int max_y = -1;
        for (int j = 0; j < 20 - current_shape[rot].size() + 1; ++j) {
            bool flag = true;
            for (int y = 0; y < current_shape[rot].size(); ++y) {
                for (int x = 0; x < current_shape[rot][0].size(); ++x) {
                    if (field[j + y][i + x] == 1 && current_shape[rot][y][x] == 1) {
                        flag = false;
                    }
                }
            }
            if (flag) {
                max_y = j;
            }
            else {
                break;
            }
        }
        if (max_y == -1) {
            return false;
        }
        else {
            return put_at(field, i, max_y, rot);
        }
    }

    int get_height(vector<vector<int>>& field, int i) {
        for (int j = 0; j < 20; ++j) {
            if (field[j][i] == 1) {
                return 20 - j;
            }
        }
        return 0;
    }

    vector<int> get_heights(vector<vector<int>>& field) {
        vector<int> heights(10);
        for (int i = 0; i < 10; ++i) {
            heights[i] = get_height(field, i);
        }
        return heights;
    }

    int get_differences(vector<int>& heights) {
        int sum = 0;
        for (int i = 0; i < heights.size() - 1; ++i) {
            sum += abs(heights[i] - heights[i + 1]);
        }
        return sum;
    }

    int get_amount_lines(vector<vector<int>>& field) {
        int sum = 0;
        for (int i = 0; i < 20; ++i) {
            bool flag = true;
            for (int j = 0; j < 10; ++j) {
                if (field[i][j] == 0) {
                    flag = false;
                    break;
                }
            }
            if (flag) sum++;
        }
        return sum;
   }

    int get_holes(vector<vector<int>>& field, vector<int>&heights) {
        int holes = 0;
        for (int i = 0; i < 10; ++i) {
            for (int j = 20 - heights[i]; j < 20; ++j) {
                if (field[j][i] == 0) {
                    holes++;
                }
            }
        }
        return holes;
    }

    int get_max_height(vector<int>& heights) {
        int m = -1;
        for (int i = 0; i < 10; ++i) {
            m = max(m, heights[i]);
        }
        return m;
    }

    int get_min_height(vector<int>& heights) {
        int m = 100;
        for (int i = 0; i < 10; ++i) {
            m = min(m, heights[i]);
        }
        return m;
    }

    pair<int, int> get_step(TetrisNet& net) {
        double result = -1e9;
        int x;
        int rota;
        for (int rot = 0; rot < current_shape.size(); ++rot) {
            for (int i = 0; i < 10 - current_shape[rot][0].size() + 1; ++i) {
                vector<vector<int>> temp_field = field;
                get_field_with_fig(temp_field, rot, i);
                Matrix tem(1, 5);
                vector<int> heights = get_heights(temp_field);
                tem.matr[0][0] = get_differences(heights);
                tem.matr[0][1] = get_holes(temp_field, heights);
                tem.matr[0][2] = get_amount_lines(temp_field);
                tem.matr[0][3] = get_min_height(heights);
                tem.matr[0][4] = get_max_height(heights);
                double res = net.forward(tem).matr[0][0];
                if (res > result) {
                    result = res;
                    x = i;
                    rota = rot;
                }
            }
        }
        return {rota, x};
    }

    double fitness(TetrisNet& net, bool flag = false) {
        field.assign(20, vector<int>(10, 0));
        score = 0;
        while (true) {
            new_shape();
            pair<int, int> step = get_step(net);
            if (!get_field_with_fig(field, step.first, step.second)) {
                break;
            }
            delete_lines();
            if (flag) {
                for (int i = 0; i < 20; ++i) {
                    for (int j = 0; j < 10; ++j) {
                        cout << field[i][j];
                    }
                    cout << endl;
                }
                cout << endl;
            }
            
        }
        net.score = score;
        return score;
    }
};