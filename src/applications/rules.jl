"""TODO: generate association rules from the group's complete frequent output.

For disjoint nonempty A, B with union X:
support = count(X)/n; confidence = count(X)/count(A);
lift = confidence/(count(B)/n). Require confidence >= minconf.
Emit all qualifying rules, not only 10. Sort by (-lift,-confidence,-support,
total_item_count,antecedent,consequent); presentation takes the first 10.
Filter minconf with exact count ratios before converting report values to floats.
"""
function association_rules(patterns::Vector{Pattern}, n::Integer;
                           minconf=3//5)::Vector{AssociationRule}
    n > 0 || throw(ArgumentError("n must be positive"))
    0 < minconf <= 1 || throw(ArgumentError("minconf must lie in (0, 1]"))
    error("TODO APPLICATION 1: implement rule generation and retain item labels")
end
