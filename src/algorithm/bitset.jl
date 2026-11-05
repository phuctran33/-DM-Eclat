"""Packed intersection with fresh ownership; never mutate either parent mask."""
intersect_tids(a::BitVector, b::BitVector)::BitVector = a .& b
tid_support(tids::BitVector) = count(tids)

"""ECLAT with BitVector tidsets and the Basic backend's ordered prefix DFS.

Count singletons first so infrequent items never allocate n-bit masks. Julia
stores BitVector data in packed words; broadcast AND and count use packed
operations/popcount. All candidate masks have exactly n bits, including tails
whose length is not a multiple of the machine word size.
"""
function mine(::BitsetBackend, transactions::Vector{Vector{Int}}, min_count::Int)
    counts = Dict{Int,Int}()
    for items in transactions, item in items
        counts[item] = get(counts, item, 0) + 1
    end
    items = sort!([item for (item, support) in counts if support >= min_count])
    vertical = Dict(item => falses(length(transactions)) for item in items)
    for (tid, transaction) in enumerate(transactions), item in transaction
        mask = get(vertical, item, nothing)
        mask === nothing || (mask[tid] = true)
    end
    atoms = BitsetAtom[BitsetAtom((item,), vertical[item]) for item in items]
    return enumerate_class!(Pattern[], atoms, min_count)
end
