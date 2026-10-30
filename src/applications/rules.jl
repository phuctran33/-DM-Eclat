"""TODO: generate association rules from the group's complete frequent output.

For disjoint nonempty A, B with union X:
support = count(X)/n; confidence = count(X)/count(A);
lift = confidence/(count(B)/n). Require confidence >= minconf.
Sort by decreasing lift with deterministic tie breaking; show top 10.
"""
function association_rules(patterns::Vector{Pattern}, n::Integer; minconf=0.6)
    n > 0 || throw(ArgumentError("n must be positive"))
    0 < minconf <= 1 || throw(ArgumentError("minconf must lie in (0, 1]"))
    error("TODO APPLICATION 1: implement rule generation and retain item labels")
end
