"""Two-pointer intersection of strictly increasing TID lists; parents stay unchanged.

Time O(length(a)+length(b)), storage O(min(length(a),length(b))).
"""
function intersect_tids(a::Vector{Int}, b::Vector{Int})::Vector{Int}
    tids = Int[]
    sizehint!(tids, min(length(a), length(b)))
    i, j = 1, 1
    @inbounds while i <= length(a) && j <= length(b)
        if a[i] == b[j]
            push!(tids, a[i])
            i += 1
            j += 1
        elseif a[i] < b[j]
            i += 1
        else
            j += 1
        end
    end
    return tids
end

tid_support(tids::Vector{Int}) = length(tids)

"""Enumerate an ordered prefix class, shared by both representations.

Atoms contain prefix+extension and its exact tidset. Joining only later siblings
creates one increasing path per itemset. Children own their tidsets; parent
classes remain read-only. DFS retains active ancestor classes, not all lattice
levels. All qualifying patterns are retained in the returned vector.
"""
function enumerate_class!(patterns::Vector{Pattern}, atoms::Vector{A},
                          min_count::Int) where {A<:Union{ListAtom,BitsetAtom}}
    for i in eachindex(atoms)
        a = atoms[i]
        push!(patterns, Pattern(a.items, tid_support(a.tids)))
        children = A[]
        for j in (i + 1):length(atoms)
            b = atoms[j]
            tids = intersect_tids(a.tids, b.tids)
            tid_support(tids) >= min_count || continue
            push!(children, A((a.items..., last(b.items)), tids))
        end
        isempty(children) || enumerate_class!(patterns, children, min_count)
    end
    return patterns
end

"""ECLAT Basic: horizontal rows → sorted vertical TID lists → prefix DFS.

TIDs are 1-based row indices; identical transactions remain independent. F2 uses
pairwise intersections rather than the paper's horizontal-recovery pair counter.
Both backends use ascending item IDs. See docs/paper-notes.md for DFS adaptation.
"""
function mine(::ListBackend, transactions::Vector{Vector{Int}}, min_count::Int)
    vertical = Dict{Int,Vector{Int}}()
    for (tid, items) in enumerate(transactions), item in items
        push!(get!(() -> Int[], vertical, item), tid)
    end
    atoms = ListAtom[ListAtom((item,), vertical[item])
                     for item in sort!(collect(keys(vertical)))
                     if length(vertical[item]) >= min_count]
    return enumerate_class!(Pattern[], atoms, min_count)
end
