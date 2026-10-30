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
end

abstract type TidsetBackend end
struct ListBackend <: TidsetBackend end
struct BitsetBackend <: TidsetBackend end

"""Sorted tid-list atom for the baseline; TIDs refer to transaction rows."""
struct ListAtom
    items::Itemset
    tids::Vector{Int}
end

"""Packed BitVector atom; all atoms in one database have equal bit length."""
struct BitsetAtom
    items::Itemset
    tids::BitVector
end
