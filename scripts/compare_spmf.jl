using EclatProject

function main(args)
    length(args) == 2 || throw(ArgumentError("Usage: scripts/compare_spmf.jl OWN.txt SPMF.txt"))
    own, reference = read_patterns.(args)
    matched = count(k -> get(own, k, -1) == reference[k], keys(reference))
    missing = setdiff(keys(reference), keys(own))
    extra = setdiff(keys(own), keys(reference))
    wrong = [k for k in intersect(keys(own), keys(reference)) if own[k] != reference[k]]
    denominator = length(union(keys(own), keys(reference)))
    rate = denominator == 0 ? 1.0 : matched / denominator
    println("reference=$(length(reference)), own=$(length(own)), exact_matches=$matched")
    println("missing=$(length(missing)), extra=$(length(extra)), wrong_support=$(length(wrong))")
    println("exact_match_rate=$rate; identical=$(own == reference)")
    for (label, entries) in [("missing", missing), ("extra", extra), ("wrong_support", wrong)]
        for key in Iterators.take(sort!(collect(entries)), 10)
            println("$label: $key")
        end
    end
    return own == reference
end

try
    exit(main(ARGS) ? 0 : 1)
catch err
    showerror(stderr, err)
    println(stderr)
    exit(2)
end
