import random

def get_the_houmwrk(houmwrk, k, seed=None):
    pom = list(houmwrk)
    n = len(pom)
    if n < 2:
        return []
    if k < 1:
        return []
    if k > n - 1:
        raise ValueError(f"k={k} je moc velké, maximum je {n-1} při n={n}")

    rng = random.Random(seed)
    rng.shuffle(pom)

    result = []
    for i in range(n):
        reviewer = pom[i]

        to_review = [pom[(i + j) % n] for j in range(1, k + 1)]
        result.append((reviewer, to_review))
    return result