"""Generate all association rules from the group's complete frequent output.

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
    # Decimal floats are interpreted through their printed decimal value; prefer
    # Rational or parse_minsup for an explicit exact confidence boundary.
    confidence = minconf isa AbstractFloat ? parse_minsup(string(minconf)) : big(minconf)
    0 < confidence <= 1 || throw(ArgumentError("minconf must lie in (0, 1]"))
    supports = Dict(p.items => p.support for p in patterns)
    length(supports) == length(patterns) || throw(ArgumentError("Duplicate itemsets"))
    all(p -> p.support <= n, patterns) || throw(ArgumentError("Support exceeds n"))
    rules = AssociationRule[]
    for p in patterns
        length(p.items) >= 2 || continue
        # Recursive subset enumeration avoids fixed-width bitmask overflow.
        antecedent, consequent = Int[], Int[]
        function split_rule!(i::Int)
            if i > length(p.items)
                (isempty(antecedent) || isempty(consequent)) && return
                a, b = Tuple(antecedent), Tuple(consequent)
                haskey(supports, a) && haskey(supports, b) ||
                    throw(ArgumentError("Complete subset support is required for $(p.items)"))
                na, nb = supports[a], supports[b]
                p.support <= min(na, nb) && p.support >= na + nb - n ||
                    throw(ArgumentError("Inconsistent subset support"))
                big(p.support) // big(na) >= confidence || return
                push!(rules, AssociationRule(a, b, p.support, na, nb, n))
                return
            end
            push!(antecedent, p.items[i])
            split_rule!(i + 1)
            pop!(antecedent)
            push!(consequent, p.items[i])
            split_rule!(i + 1)
            pop!(consequent)
        end
        split_rule!(1)
    end
    sort!(rules; by=r -> (-r.lift, -r.confidence, -r.support,
                         length(r.antecedent) + length(r.consequent),
                         r.antecedent, r.consequent))
    return rules
end
