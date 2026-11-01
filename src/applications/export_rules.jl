"""Export caller-supplied rules under schema v1; does not perform FIM or rule generation."""
function write_association_rules(path::AbstractString, dataset::PreparedDataset,
                                 rules::Vector{AssociationRule}; top_k::Union{Nothing,Int}=nothing)
    top_k === nothing || top_k >= 1 || throw(ArgumentError("top_k must be positive"))
    ordered = sort(rules; by=r -> (-r.lift,-r.confidence,-r.support,
        length(r.antecedent)+length(r.consequent),r.antecedent,r.consequent))
    allunique((r.antecedent,r.consequent) for r in ordered) || throw(ArgumentError("Duplicate association rule"))
    for rule in ordered
        rule.n_transactions == length(dataset.transactions) || throw(ArgumentError("Rule denominator differs from dataset size"))
        all(id -> haskey(dataset.item_labels,id),(rule.antecedent...,rule.consequent...)) ||
            throw(ArgumentError("Rule contains unmapped item"))
    end
    limit = top_k === nothing ? length(ordered) : min(top_k,length(ordered))
    header = ("rank","antecedent_ids","consequent_ids","antecedent_labels","consequent_labels",
              "length","support_count","antecedent_count","consequent_count","n_transactions",
              "support","confidence","lift")
    rows = ((i,join(rule.antecedent,' '),join(rule.consequent,' '),
             join((dataset.item_labels[id] for id in rule.antecedent)," | "),
             join((dataset.item_labels[id] for id in rule.consequent)," | "),
             length(rule.antecedent)+length(rule.consequent),rule.support_count,rule.antecedent_count,
             rule.consequent_count,rule.n_transactions,rule.support,rule.confidence,rule.lift)
            for (i,rule) in enumerate(ordered[1:limit]))
    return write_csv_table(path,header,rows)
end
