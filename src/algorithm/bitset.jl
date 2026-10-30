"""TODO: packed BitVector backend with the SAME enumeration semantics.

Compare list intersection with bitwise AND + count. Avoid creating full masks
for infrequent singleton items. Measure peak RSS separately from allocations.
"""
function mine(::BitsetBackend, transactions::Vector{Vector{Int}}, min_count::Int)
    # TODO: preserve baseline's candidate generation and threshold policy.
    # TODO: implement safe buffer ownership to avoid modifying a parent's mask.
    # TODO: benchmark sparse/dense cases; bitsets are not always a speedup.
    error("TODO ECLAT: implement and measure the optimized BitVector backend")
end
