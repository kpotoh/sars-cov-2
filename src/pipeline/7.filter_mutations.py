"""
Substitutions contexts of parent and child sequences must be equal
"""

import pandas as pd


def main():
    path_to_mut = "./data/mutation_dists.csv"
    extra_col = "phylo_dist"

    new_path = path_to_mut.replace("csv", "filtered.csv")
    assert path_to_mut != new_path, "something wrong with path"

    mut: pd.DataFrame = pd.read_csv(path_to_mut)
    mut = mut[(~mut.parent_nucl_context.str.contains('-')) &
              (~mut.child_nucl_context.str.contains('-'))]

    large_parent_context = mut.parent_nucl_context.str.slice(
        0, 2) + mut.parent_nucl_context.str.slice(3, 5)
    large_child_context = mut.child_nucl_context.str.slice(
        0, 2) + mut.child_nucl_context.str.slice(3, 5)

    mut = mut[large_parent_context == large_child_context]

    if extra_col in mut.columns:
        mut.drop(extra_col, axis=1, inplace=True)

    mut.to_csv(new_path, index=None)


if __name__ == "__main__":
    main()