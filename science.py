import argparse
import itertools
from functools import lru_cache
from random import random, seed

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

from soldier import Soldier, StatSwap, StatSwapper
from main import generate_sample

# Generated with `python main.py -n 1000000 --init lwotc --stat`
LWOTC_MEAN = [64.595764, 14.926747, 4.204107, 29.911448, 4.761862, 5.337548, 19.631602]
LWOTC_COV = [21.73851099, 1.42541642, 1.12657446, 57.12975367, 56.76390906, 8.00595135, 68.85382777]
LWOTC_SKEW = [0.02939368, 0.22004164, 0.62944555, 0.00833649, 0.02128133, 0.68264077, 0.04893522]

def fitness(x, n, parameter):
    return memoized_fitness(tuple(x), n, parameter)

@lru_cache
def memoized_fitness(x, n, parameter):
    # random.seed(0)
    sample = generate_sample(
        n,
        StatSwapper(
            5*(4,),
            list(
                (StatSwap(stat, amount, stat, 0, weight) for weight, (amount, stat) in zip(x, itertools.product(range(1, args.parameter+1), Soldier.STATS)))
            )
        )
    )
    mean = sample.mean(0)
    cov = np.diag(np.cov(sample.T))
    # skew = scipy.stats.skew(sample)

    mean_fit = sum(2 * (lwotc_mu - sample_mu)**2 / (range_.max_delta - range_.min_delta) for lwotc_mu, sample_mu, range_ in zip(LWOTC_MEAN, mean, Soldier.STATS.values()))
    cov_fit = sum((lwotc_cov - sample_cov)**2 / lwotc_cov for lwotc_cov, sample_cov in zip(LWOTC_COV, cov))
    return mean_fit + cov_fit

def fitness_cov_ratios(x, n):
    return memoized_fitness_cov_ratios(tuple(x), n)

@lru_cache
def memoized_fitness_cov_ratios(x, n):
    # random.seed(0)
    sample = generate_sample(
        n,
        StatSwapper(
            5*(4,),
            list(
                (StatSwap(stat, 1, stat, 0, weight) for weight, stat in zip(x, Soldier.STATS))
            )
        )
    )

    cov = np.diag(np.cov(sample.T))
    return sum((lwotc_cov / sum(LWOTC_COV) - sample_cov / sum(cov))**2  for lwotc_cov, sample_cov in zip(LWOTC_COV, cov))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--number", type=int, help="Number of soldiers to generate per batch", required=True
    )
    parser.add_argument(
        "-e", "--experiment", type=int, help="Which experiment to run", required=True
    )
    parser.add_argument(
        "-p", "--parameter", type=int, help="Parameter to apply to the experiment", default=1
    )

    args = parser.parse_args()

    match args.experiment:
        case 1:
            result = sp.optimize.minimize(
                fitness,
                [1]*len(Soldier.STATS)*args.parameter, args=(args.number, args.parameter),
                method="Nelder-Mead",
                callback=lambda *args, **kwargs: print(args, kwargs),
            )
            print(result)

        case 2:
            result = sp.optimize.minimize(
                fitness_cov_ratios,
                [1]*len(Soldier.STATS), args=(args.number,),
                method="Nelder-Mead",
                callback=lambda *args, **kwargs: print(args, kwargs),
            )
            print(result)

        case 3:
            d = len(Soldier.STATS)
            p = args.parameter
            weights = np.ndarray([p, d], dtype=np.float64)
            covs = np.ndarray([p, d], dtype=np.float64)
            for i in range(p):
                roll = sorted(random() for __ in range(d-1))
                roll = list(x - y for x, y in zip(roll + [1], [0] + roll))
                weights[i, :] = roll
                sample = generate_sample(
                    args.number,
                    StatSwapper(
                        5*(4,),
                        list(
                            StatSwap(stat, 1, stat, 0, weight) for weight, stat in zip(roll, Soldier.STATS)
                        )
                    )
                )
                covs[i, :] = np.diag(np.cov(sample.T))
            ax = plt.subplot()
            for i, (w, c) in enumerate(zip(weights.T, covs.T)):
                ax.scatter(w, c, marker=".")
            ax.legend(Soldier.STATS)
            plt.show()
