import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_probability = dict()
    names = set(people.keys())
    conditions = {
        name: {
            "gene": 1 if name in one_gene else
            2 if name in two_genes else 0,
            "trait": True if name in have_trait else False
        }
        for name in names
    }
    for person in people:
        if not people[person]["mother"] and not people[person]["father"]:
            if person in one_gene and person in have_trait:
                joint_probability[person] = PROBS["gene"][1] * PROBS["trait"][1][True]
            if person in two_genes and person in have_trait:
                joint_probability[person] = PROBS["gene"][2] * PROBS["trait"][2][True]
            if person not in two_genes and person not in one_gene and person in have_trait:
                joint_probability[person] = PROBS["gene"][0] * PROBS["trait"][0][True]
            if person in one_gene and person not in have_trait:
                joint_probability[person] = PROBS["gene"][1] * PROBS["trait"][1][False]
            if person in two_genes and person not in have_trait:
                joint_probability[person] = PROBS["gene"][2] * PROBS["trait"][2][False]
            if person not in two_genes and person not in one_gene and person not in have_trait:
                joint_probability[person] = PROBS["gene"][0] * PROBS["trait"][0][False]
        elif people[person]["mother"] and people[person]["father"]:
            gene_num = conditions[person]["gene"]
            mum = people[person]["mother"]
            dad = people[person]["father"]
            mum_gene = conditions[mum]["gene"]
            dad_gene = conditions[dad]["gene"]
            temp_pros = 1
            if gene_num == 0:
                temp_pros *= calculate_children_gene(mum_gene, False)
                temp_pros *= calculate_children_gene(dad_gene, False)
            elif gene_num == 1:
                temp_pros *= (calculate_children_gene(mum_gene, False) * calculate_children_gene(dad_gene, True)
                              + calculate_children_gene(dad_gene, True) * calculate_children_gene(dad_gene, False))
            else:
                temp_pros *= calculate_children_gene(mum_gene, True)
                temp_pros *= calculate_children_gene(dad_gene, True)
            if person in have_trait:
                joint_probability[person] = temp_pros * PROBS["trait"][gene_num][True]
            elif person not in have_trait:
                joint_probability[person] = temp_pros * PROBS["trait"][gene_num][False]
    final_pros = 1
    for person in joint_probability:
        final_pros *= joint_probability[person]
    return final_pros


def calculate_children_gene(parent_gene, child_gene):
    if child_gene:
        if parent_gene == 0:
            return PROBS["mutation"]
        if parent_gene == 1:
            return 0.5
        if parent_gene == 2:
            return 1 - PROBS["mutation"]
    else:
        if parent_gene == 0:
            return 1 - PROBS["mutation"]
        if parent_gene == 1:
            return 0.5  # in this case the pros of both gene is equal
        if parent_gene == 2:
            return PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    names = set(probabilities.keys())
    conditions = {
        name: {
            "gene": 1 if name in one_gene else
            2 if name in two_genes else 0,
            "trait": True if name in have_trait else False
        }
        for name in names
    }
    for person in probabilities:
        probabilities[person]["gene"][conditions[person]["gene"]] += p
        probabilities[person]["trait"][conditions[person]["trait"]] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        no_gene = probabilities[person]["gene"][0]
        one_gene = probabilities[person]["gene"][1]
        two_gene = probabilities[person]["gene"][2]
        trait_true = probabilities[person]["trait"][True]
        trait_false = probabilities[person]["trait"][False]
        probabilities[person]["gene"][0] = no_gene / (no_gene + one_gene + two_gene)
        probabilities[person]["gene"][1] = one_gene / (no_gene + one_gene + two_gene)
        probabilities[person]["gene"][2] = two_gene / (no_gene + one_gene + two_gene)
        probabilities[person]["trait"][True] = trait_true / (trait_true + trait_false)
        probabilities[person]["trait"][False] = trait_false / (trait_true + trait_false)


if __name__ == "__main__":
    main()
