import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()
    for link in corpus.keys():
        probability_distribution[link] = (1 - damping_factor) / len(corpus.keys())
    possible_links = corpus[page]
    if possible_links:
        for link in possible_links:
            probability_distribution[link] += damping_factor / len(possible_links)
    else:
        for link in corpus.keys():
            probability_distribution[link] = damping_factor / len(corpus.keys())
    if sum(probability_distribution.values()) != 1.0:
        probability_distribution[link] += 1 - sum(probability_distribution.values())
    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    for page in corpus.keys():
        pagerank[page] = 0
    initial_sample = random.choice(list(corpus.keys()))
    pagerank[initial_sample] = 1
    for i in range(1, n):
        probability_distribution = transition_model(corpus, initial_sample, damping_factor)
        random_sample = random.choices(list(probability_distribution.keys()), list(probability_distribution.values()))
        pagerank[random_sample[0]] += 1
        initial_sample = random_sample[0]
    for page in pagerank:
        pagerank[page] /= n
    if sum(pagerank.values()) != 1.0:
        raise ValueError("Pagerank values do not sum to 1.0")
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    new_pagerank = dict()
    for page in corpus.keys():
        pagerank[page] = 1 / len(corpus.keys())
        new_pagerank[page] = 1 / len(corpus.keys())
    threshold = 0.001
    N = len(corpus.keys())
    iter_error = 1
    while iter_error >= threshold:
        pagerank = copy.deepcopy(new_pagerank)
        for new_page in new_pagerank:
            temp_sum = 0
            iter_error = 1
            for page in pagerank:
                if new_page in corpus[page]:
                    temp_sum += pagerank[page] / len(corpus[page])
                if not corpus[page]:
                    temp_sum += pagerank[page] / N
            new_pagerank[new_page] = (1 - damping_factor) / N + damping_factor * temp_sum
        for page in pagerank.keys():
            iter_error = abs(new_pagerank[page] - pagerank[page])
    if sum(new_pagerank.values()) > 1.0:
        new_pagerank['1.html'] -= sum(new_pagerank.values()) - 1.0
    elif sum(new_pagerank.values()) < 1.0:
        new_pagerank['1.html'] += 1.0 - sum(new_pagerank.values())
    return new_pagerank


if __name__ == "__main__":
    main()
