"""TODO (B, M2): UCI Splice -> position/base transactions and EI/IE/N labels.

Working proposal: take positions 25:36 of a 60-base sequence (Julia 1-based),
six bases on either side of the central 30|31 boundary. Confirm with the group's
dataset version. Encode a token as (relative_position, base), not base alone.
Store class label as separate metadata, not a mined item. Handle ambiguity
explicitly and record per-class counts before/after filtering.
"""
function splice_transactions(path::AbstractString; positions=25:36)
    length(positions) == 12 || throw(ArgumentError("The group plan uses 12 positions"))
    error("TODO M2 / B: implement Splice parser, position/base mapping and class metadata")
end

"""TODO: compare class-specific support for shared 2–4-item patterns.

Mine complete frequent outputs first; filter 2–4-item patterns for presentation.
When a candidate is infrequent/absent in another class, count it directly there;
absence from that class's frequent output does NOT imply zero support.
"""
function compare_dna_patterns(transactions, labels, patterns)
    error("TODO M2 / B: compare EI, IE, N with class-specific denominators")
end
