"""Mine complete outputs with both group backends; fail before reporting a mismatch."""
function verified_application_patterns(transactions::Vector{Vector{Int}}, min_count::Int)
    basic = mine(transactions, min_count; backend=:list)
    optimized = mine(transactions, min_count; backend=:bitset)
    Dict(p.items => p.support for p in basic) == Dict(p.items => p.support for p in optimized) ||
        error("Application correctness failure: list and bitset outputs differ")
    return basic
end

"""Complete Groceries mining and rule generation under the frozen ranking contract."""
function groceries_application(dataset::PreparedDataset; minsup="0.005", minconf="0.60", top_k=10)
    dataset.dataset_id == "groceries" && dataset.classes === nothing ||
        throw(ArgumentError("Expected an unlabelled groceries PreparedDataset"))
    isempty(dataset.transactions) && throw(ArgumentError("Groceries must contain at least one basket"))
    top_k isa Integer && top_k >= 1 || throw(ArgumentError("top_k must be a positive integer"))
    threshold = minimum_count(parse_minsup(minsup), length(dataset.transactions))
    confidence = parse_minsup(minconf)
    patterns = verified_application_patterns(dataset.transactions, threshold)
    rules = association_rules(patterns, length(dataset.transactions); minconf=confidence)
    return (patterns=patterns, rules=rules, top10=rules[1:min(top_k,length(rules))],
            min_count=threshold, minconf=confidence)
end

"""Mine each DNA class completely, then recount the union of 2–4-item candidates."""
function dna_application(dataset::PreparedDataset; minsup="0.20")
    dataset.dataset_id == "splice" && dataset.classes !== nothing ||
        throw(ArgumentError("Expected a labelled splice PreparedDataset"))
    relative = parse_minsup(minsup)
    patterns = Dict{String,Vector{Pattern}}()
    thresholds = Dict{String,Int}()
    for label in DNA_CLASSES
        transactions = dataset.transactions[findall(==(label), dataset.classes)]
        isempty(transactions) && throw(ArgumentError("DNA class $label must be nonempty"))
        thresholds[label] = minimum_count(relative, length(transactions))
        patterns[label] = verified_application_patterns(transactions, thresholds[label])
    end
    comparisons = compare_dna_patterns(dataset, patterns)
    return (patterns_by_class=patterns, comparisons=comparisons, min_counts=thresholds)
end
