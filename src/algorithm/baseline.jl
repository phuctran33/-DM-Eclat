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

Each atom holds an extension item and the exact tidset of prefix plus extension.
Joining only later siblings gives one increasing path per itemset. The search
reuses its prefix vector; each emitted pattern owns an immutable key. Children
own their tidsets and do not mutate their parents.
"""
function enumerate_class!(patterns::Vector{Pattern}, prefix::Vector{Int},
                          atoms::Vector{A}, min_count::Int) where {A<:Union{ListAtom,BitsetAtom}}
    for i in eachindex(atoms)
        a = atoms[i]
        push!(prefix, a.item)
        push!(patterns, Pattern(prefix, tid_support(a.tids), Val(:dfs_prefix)))
        children = A[]
        for j in (i + 1):length(atoms)
            b = atoms[j]
            tids = intersect_tids(a.tids, b.tids)
            tid_support(tids) >= min_count || continue
            push!(children, A(b.item, tids))
        end
        isempty(children) || enumerate_class!(patterns, prefix, children, min_count)
        pop!(prefix)
    end
    return patterns
end

"""ECLAT Basic: horizontal rows → sorted vertical TID lists → prefix DFS.

TIDs are 1-based row indices; identical transactions remain independent. F2 uses
pairwise intersections rather than the paper's horizontal-recovery pair counter.
Both backends use ascending item IDs. See docs/ARCHITECTURE.md#zaki for the DFS adaptation.
"""
function mine(::ListBackend, transactions::Vector{Vector{Int}}, min_count::Int)
    vertical = Dict{Int,Vector{Int}}()
    for (tid, items) in enumerate(transactions), item in items
        push!(get!(() -> Int[], vertical, item), tid)
    end
    atoms = ListAtom[ListAtom(item, vertical[item])
                     for item in sort!(collect(keys(vertical)))
                     if length(vertical[item]) >= min_count]
    return enumerate_class!(Pattern[], Int[], atoms, min_count)
end
