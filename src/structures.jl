"""Canonical key: increasing positive item IDs, with no duplicates."""
const Itemset = Tuple{Vararg{Int}}

struct Pattern
    items::Itemset
    support::Int
    function Pattern(items, support::Integer)
        key = Tuple(sort!(collect(Int, items)))
        isempty(key) && throw(ArgumentError("An itemset must be nonempty"))
        all(>(0), key) || throw(ArgumentError("Item IDs must be positive"))
        length(unique(key)) == length(key) || throw(ArgumentError("Duplicate items"))
        support > 0 || throw(ArgumentError("Support must be positive"))
        new(key, Int(support))
    end

    # DFS visits strictly increasing positive IDs and emits only positive supports.
    # Capture the reused prefix before enumeration advances to the next sibling.
    Pattern(prefix::Vector{Int}, support::Int, ::Val{:dfs_prefix}) = new(Tuple(prefix), support)
end

abstract type TidsetBackend end
struct ListBackend <: TidsetBackend end
struct BitsetBackend <: TidsetBackend end

"""Extension item and its full itemset's sorted transaction IDs."""
struct ListAtom
    item::Int
    tids::Vector{Int}
end

"""Extension item and its full itemset's packed transaction mask."""
struct BitsetAtom
    item::Int
    tids::BitVector
end
