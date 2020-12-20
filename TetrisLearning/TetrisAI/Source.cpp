#include <iostream>
#include "Matrix.h"
#include "TetrisNet.h"
#include "Tetris.h"
#include <random>
#include <vector>
#include <algorithm>

using namespace std;

TetrisNet create_new_individual(int input, int hidden, int output) {
    TetrisNet net(input, hidden, output);
    net.randomize();
    return net;
}

vector<TetrisNet> create_individuals(int amount, int input, int hidden, int output) {
    vector<TetrisNet> population;
    for (int i = 0; i < amount; ++i) {
        population.push_back(create_new_individual(input, hidden, output));
    }
    return population;
}

void fitnesses(vector<TetrisNet>& individuals, Tetris& tetris) {
    for (int i = 0; i < individuals.size(); ++i) {
        if (!individuals[i].flag) {
            tetris.fitness(individuals[i]);
        }
    }
}



int main() {
    Tetris tetris;
    int input = 5;
    int hidden = 5;
    int output = 1;
    TetrisNet net(input, hidden, output);
    net.randomize();
    tetris.fitness(net);
    int amount = 200;
    double percentage_survivors = 0.5;
    double mutagen_perc = 0.05;
    double epochs = 100;
    vector<TetrisNet> population = create_individuals(amount, input, hidden, output);
    for (int i = 0; i < epochs; ++i) {
        fitnesses(population, tetris);
        sort(population.rbegin(), population.rend());
        cout << "Epocha: " << i << ". Max value:" << population[0].score << endl;
        cout << "Weights:" << endl;
        cout << "[";
        for (int i = 0; i < population[0].m1.rows(); ++i) {
            cout << "[";
            for (int j = 0; j < population[0].m1.columns(); ++j) {
                cout << population[0].m1.matr[i][j] << ", ";
            }
            cout << "]," << endl;
        }
        cout << "]" << endl;
        cout << "[";
        for (int i = 0; i < population[0].bias1.rows(); ++i) {
            cout << "[";
            for (int j = 0; j < population[0].bias1.columns(); ++j) {
                cout << population[0].bias1.matr[i][j] << ", ";
            }
            cout << "]," << endl;
        }
        cout << "]" << endl;
        cout << "[";
        for (int i = 0; i < population[0].m2.rows(); ++i) {
            cout << "[";
            for (int j = 0; j < population[0].m2.columns(); ++j) {
                cout << population[0].m2.matr[i][j] << ", ";
            }
            cout << "]," << endl;
        }
        cout << "]" << endl;
        cout << "[";
        for (int i = 0; i < population[0].bias2.rows(); ++i) {
            cout << "[";
            for (int j = 0; j < population[0].bias2.columns(); ++j) {
                cout << population[0].bias2.matr[i][j] << ", ";
            }
            cout << "]," << endl;
        }
        cout << "]" << endl;
        cout << endl;
        int new_surv = percentage_survivors * amount;
        for (int i = 0; i < new_surv; ++i) {
            population.pop_back();
        }
        int surv = amount - new_surv;
        while (population.size() < amount) {
            random_device randomDevice;
            mt19937 randomGen(randomDevice());
            uniform_int_distribution<> uni(0, surv-1);
            int p1 = uni(randomGen);
            int p2 = uni(randomGen);
            TetrisNet net(input, hidden, output);
            bernoulli_distribution bern(0.5);
            for (int i = 0; i < population[0].m1.rows(); ++i) {
                for (int j = 0; j < population[0].m1.columns(); ++j) {
                    if (bern(randomGen)) {
                        net.m1.matr[i][j] = population[p1].m1.matr[i][j];
                    }
                    else {
                        net.m1.matr[i][j] = population[p2].m1.matr[i][j];
                    }
                }
            }
            for (int i = 0; i < population[0].bias1.rows(); ++i) {
                for (int j = 0; j < population[0].bias1.columns(); ++j) {
                    if (bern(randomGen)) {
                        net.bias1.matr[i][j] = population[p1].bias1.matr[i][j];
                    }
                    else {
                        net.bias1.matr[i][j] = population[p2].bias1.matr[i][j];
                    }
                }
            }
            for (int i = 0; i < population[0].m2.rows(); ++i) {
                for (int j = 0; j < population[0].m2.columns(); ++j) {
                    if (bern(randomGen)) {
                        net.m2.matr[i][j] = population[p1].m2.matr[i][j];
                    }
                    else {
                        net.m2.matr[i][j] = population[p2].m2.matr[i][j];
                    }
                }
            }
            for (int i = 0; i < population[0].bias2.rows(); ++i) {
                for (int j = 0; j < population[0].bias2.columns(); ++j) {
                    if (bern(randomGen)) {
                        net.bias2.matr[i][j] = population[p1].bias2.matr[i][j];
                    }
                    else {
                        net.bias2.matr[i][j] = population[p2].bias2.matr[i][j];
                    }
                }
            }
            net.mutant(mutagen_perc);
            population.push_back(net);
        }
    }
}