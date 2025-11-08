from itertools import permutations

def permutate(v):
    """Return all permutations of a list."""
    return list(permutations(v))

def fit_perm(to_fit, taken_intervals, left_bound, right_bound):
    """Try to fit the intervals to_fit into the open spaces defined by taken_intervals."""
    open_intervals = []
    left = left_bound
    
    for l, r in taken_intervals:
        if left > right_bound:
            break
        if left < l:
            open_intervals.append([left, l - 1])
        left = r + 1
    
    if left <= right_bound:
        open_intervals.append([left, right_bound])
    
    res = []
    idx = 0
    for f in to_fit:
        while idx < len(open_intervals) and open_intervals[idx][1] - open_intervals[idx][0] + 1 < f:
            idx += 1
        if idx < len(open_intervals):
            res.append((open_intervals[idx][0], open_intervals[idx][0] + f - 1))
            open_intervals[idx][0] += f  # shorten the open interval
        else:
            return []
    
    return res

def fit_intervals(intervals_to_fit, taken_intervals, left_bound, right_bound):
    """Try all permutations of intervals_to_fit to see if they fit."""
    for perm in permutate(intervals_to_fit):
        fit = fit_perm(perm, taken_intervals, left_bound, right_bound)
        if fit:
            return fit
    return []

def generate_intervals(left_bound, right_bound, taken_intervals, intervals_to_add):
    """Generate the maximal set of intervals that fit into the bounds."""
    taken_intervals = sorted(taken_intervals)
    answer_intervals = []
    
    n = len(intervals_to_add)
    for mask in range(1 << n):
        subset_intervals_to_add = [intervals_to_add[i] for i in range(n) if mask & (1 << i)]
        generated_intervals = fit_intervals(subset_intervals_to_add, taken_intervals, left_bound, right_bound)
        if len(generated_intervals) > len(answer_intervals):
            answer_intervals = generated_intervals
    
    return answer_intervals
