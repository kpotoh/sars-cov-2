import argparse
import sys
from typing import Dict, Iterable, List, Tuple, Union

import pandas as pd
import scipy.stats
import statsmodels.api as sm

PATH_TO_MUTSPEC = "/home/mr/Sars_Cov_2_MutSpec/Sars_Cov_2/new_data/data_obtained/07.MutSpec12_ForFullGenome.csv"
COLS = ["NucSubst", "ExpFr", "ObsFr", "ObsToExp"]
NUCLEOTIDES = list("ACGU")

directional_pairs = [
    ("A>C", "C>A"),
    ("A>G", "G>A"),
    ("A>U", "U>A"),
    ("C>G", "G>C"),
    ("C>U", "U>C"),
    ("G>U", "U>G"),
]
reciprocal_pairs = [
    ("A>C", "U>G"),
    ("A>G", "U>C"),
    ("A>U", "U>A"),
    ("C>G", "G>C"),
    ("C>U", "G>A"),
    ("G>U", "C>A"),
]


def asterics_for_vector(pvals: Iterable) -> List[str]:
    asterics = []
    for val in pvals:
        if val < 0.001:
            asterics.append("***")
        elif val < 0.01:
            asterics.append("**")
        elif val < 0.05:
            asterics.append("*")
        else:
            asterics.append("")
    return asterics


def binom_testing(
        pairs: List[Tuple[str]],
        mut_num: Dict[str, Union[int, float]],
        label: str = None):
    data = []
    for mut1, mut2 in pairs:
        n1, n2 = round(mut_num[mut1]), round(mut_num[mut2])
        res = scipy.stats.binomtest(n1, n1 + n2, p=0.5)
        pval = res.pvalue
        row = (mut1, mut2, pval) if label is None else (
            label, mut1, mut2, pval)
        data.append(row)
    cols = ["mut1", "mut2", "pval"] if label is None else [
        "label", "mut1", "mut2", "pval"]
    data = pd.DataFrame(data, columns=cols)

    _, qval, _, _ = sm.stats.multipletests(
        data["pval"].values, method="fdr_bh")  # adjust pval
    data["qval"] = qval
    data["asterics"] = asterics_for_vector(qval)
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Do statistics (binomial test) for 12-comp. mutspec distinct values.\n"
        "For each pair of reciprocal and directional substitutions count significance of its difference"
    )
    parser.add_argument("inp", type=argparse.FileType("r"),
                        help="path to input MutSpec table")
    parser.add_argument(
        "out", default=None, nargs="?", type=argparse.FileType("w"),
        help="path to output csv with statistics, (by default write file in the same dir: `inp`.compared.csv)"
    )
    args = parser.parse_args()

    inp = args.inp
    out = args.out or inp.name.replace(".csv", ".compared.csv")
    print(f"input file: {inp.name}", file=sys.stderr)
    print(
        f"output file: {out if isinstance(out, str) else out.name}", file=sys.stderr)

    mutspec = pd.read_csv(inp, usecols=COLS)
    mut_num = dict(zip(mutspec.NucSubst, mutspec.ObsToExp))

    dirp = binom_testing(directional_pairs, mut_num, "directional")
    recp = binom_testing(reciprocal_pairs, mut_num, "reciprocal")

    compared = pd.concat([dirp, recp], axis=0).reset_index(drop=True)
    compared.to_csv(out, index=None)


if __name__ == "__main__":
    main()
