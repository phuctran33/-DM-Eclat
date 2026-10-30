"""Shared contracts; docs/SCHEMA.md is the normative v1.0.0 specification."""
const SCHEMA_VERSION = "1.0.0"
const DNA_CLASSES = ("EI", "IE", "N")
const DNA_POSITIONS = 25:36
const DNA_BASE_ORDER = ('A', 'C', 'G', 'T')

"""Preprocessor output. Metadata follows transaction order; unused mapping IDs are allowed."""
struct PreparedDataset
    dataset_id::String
    transactions::Vector{Vector{Int}}
    item_labels::Dict{Int,String}
    row_ids::Vector{String}
    classes::Union{Nothing,Vector{String}}

    function PreparedDataset(dataset_id::AbstractString,
                             transactions::Vector{Vector{Int}},
                             item_labels::Dict{Int,String}, row_ids::Vector{String};
                             classes::Union{Nothing,Vector{String}}=nothing)
        isempty(strip(dataset_id)) && throw(ArgumentError("dataset_id is required"))
        n = length(transactions)
        length(row_ids) == n || throw(ArgumentError("row_ids must align with transactions"))
        all(id -> !isempty(strip(id)), row_ids) && allunique(row_ids) ||
            throw(ArgumentError("row_ids must be nonempty and unique"))
        sort!(collect(keys(item_labels))) == collect(1:length(item_labels)) ||
            throw(ArgumentError("Item mapping must have contiguous IDs starting at 1"))
        all(label -> !isempty(strip(label)), values(item_labels)) && allunique(values(item_labels)) ||
            throw(ArgumentError("Item labels must be nonempty and unique"))
        for items in transactions
            !isempty(items) && issorted(items) && allunique(items) &&
                all(id -> haskey(item_labels, id), items) ||
                throw(ArgumentError("Prepared transactions must be nonempty, sorted, unique and mapped"))
        end
        if classes !== nothing
            length(classes) == n || throw(ArgumentError("classes must align with transactions"))
            all(label -> label in DNA_CLASSES, classes) ||
                throw(ArgumentError("DNA classes must be EI, IE or N"))
        end
        # Own the validated data; later changes to caller buffers cannot corrupt the contract.
        new(String(dataset_id), deepcopy(transactions), copy(item_labels), copy(row_ids),
            classes === nothing ? nothing : copy(classes))
    end
end

"""One association rule. All ratios are derived from counts, not accepted as inputs."""
struct AssociationRule
    antecedent::Itemset
    consequent::Itemset
    support_count::Int
    antecedent_count::Int
    consequent_count::Int
    n_transactions::Int
    support::Float64
    confidence::Float64
    lift::Float64

    function AssociationRule(antecedent, consequent, support_count::Integer,
                             antecedent_count::Integer, consequent_count::Integer,
                             n_transactions::Integer)
        a = Pattern(antecedent, 1).items
        b = Pattern(consequent, 1).items
        isempty(intersect(a, b)) || throw(ArgumentError("Rule sides must be disjoint"))
        n, joint, na, nb = Int.((n_transactions, support_count, antecedent_count, consequent_count))
        1 <= joint <= min(na, nb) && max(na, nb) <= n && joint >= na + nb - n ||
            throw(ArgumentError("Inconsistent rule support counts"))
        new(a, b, joint, na, nb, n, joint / n, joint / na, (joint / na) / (nb / n))
    end
end

"""Class comparison of one 2–4-item candidate; zero count in a class is valid."""
struct DNAPatternComparison
    items::Itemset
    count_EI::Int
    count_IE::Int
    count_N::Int
    n_EI::Int
    n_IE::Int
    n_N::Int
    support_EI::Float64
    support_IE::Float64
    support_N::Float64
    support_span::Float64

    function DNAPatternComparison(items, count_EI::Integer, count_IE::Integer,
                                  count_N::Integer, n_EI::Integer, n_IE::Integer, n_N::Integer)
        key = Pattern(items, 1).items
        2 <= length(key) <= 4 || throw(ArgumentError("DNA display patterns must have 2–4 items"))
        counts = Int.((count_EI, count_IE, count_N))
        sizes = Int.((n_EI, n_IE, n_N))
        all(i -> sizes[i] > 0 && 0 <= counts[i] <= sizes[i], 1:3) ||
            throw(ArgumentError("Each class needs a positive denominator and valid count"))
        supports = counts ./ sizes
        new(key, counts..., sizes..., supports..., maximum(supports) - minimum(supports))
    end
end
