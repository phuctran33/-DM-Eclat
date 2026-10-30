"""TODO: implement Eclat with sorted tid-lists from Zaki (2000).

Contract: emit ALL nonempty frequent itemsets and their absolute support once.
See docs/paper-notes.md for sections 4.1, 4.2, 5.1, 5.2 and 5.4.
The group plan chooses DFS prefix extension. Document this adaptation separately
from the paper's bottom-up traversal within classes; preserve vertical tidsets,
prefix partition and complete frequent-itemset enumeration.
"""
function mine(::ListBackend, transactions::Vector{Vector{Int}}, min_count::Int)
    # TODO 1: horizontal input -> vertical sorted tid-lists, compute F1.
    # TODO 2: choose a fixed item ordering and document F2 construction.
    # TODO 3: extend a prefix only with later items (one canonical path/itemset).
    # TODO 4: intersect TIDs, emit support >= min_count, prune other extensions.
    # TODO 5: recurse depth-first within each prefix class; release child lists.
    # TODO 6: return Vector{Pattern}; canonical keys, no empty set or duplicates.
    error("TODO ECLAT: implement the baseline from the paper before mining")
end
