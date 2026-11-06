function dna_item_labels()
    positions = [-6,-5,-4,-3,-2,-1,1,2,3,4,5,6]
    return Dict(4*(slot-1)+base_index =>
        "pos=$(position > 0 ? "+" : "")$position;base=$base"
        for (slot,position) in enumerate(positions) for (base_index,base) in enumerate(DNA_BASE_ORDER))
end

"""Read UCI Splice raw records; audit ambiguity only in the frozen 12-base window."""
function prepare_splice(path::AbstractString; positions=DNA_POSITIONS)
    collect(positions) == collect(DNA_POSITIONS) ||
        throw(ArgumentError("Schema v1 fixes the DNA window to positions 25:36"))
    transactions, row_ids, labels, sources = Vector{Int}[], String[], String[], String[]
    kept = Dict(label => 0 for label in DNA_CLASSES)
    dropped = Dict(label => 0 for label in DNA_CLASSES)
    for (line, fields) in csv_records(path)
        length(fields) == 3 || throw(ArgumentError("$path:$line: expected class,source_id,sequence"))
        label, source = uppercase(strip(fields[1])), strip(fields[2])
        label in DNA_CLASSES || throw(ArgumentError("$path:$line: unknown DNA class"))
        isempty(source) && throw(ArgumentError("$path:$line: empty source_id"))
        sequence = uppercase(replace(fields[3], r"\s+" => ""))
        length(sequence) == 60 || throw(ArgumentError("$path:$line: sequence must have 60 bases"))
        all(c -> c in "ACGTRYSWKMBDHVN", sequence) ||
            throw(ArgumentError("$path:$line: invalid IUPAC DNA symbol"))
        window = collect(sequence)[DNA_POSITIONS]
        if any(base -> !(base in DNA_BASE_ORDER), window)
            dropped[label] += 1
            continue
        end
        items = [4*(slot-1)+findfirst(==(base), DNA_BASE_ORDER) for (slot,base) in enumerate(window)]
        push!(transactions, items)
        push!(row_ids, "splice:$line")
        push!(labels, label)
        push!(sources, source)
        kept[label] += 1
    end
    all(label -> kept[label] > 0, DNA_CLASSES) ||
        throw(ArgumentError("Every DNA class EI/IE/N must retain at least one valid sample"))
    dataset = PreparedDataset("splice", transactions, dna_item_labels(), row_ids; classes=labels)
    audit = [(SCHEMA_VERSION,"splice",label,reason,counts[label])
             for label in DNA_CLASSES for (reason,counts) in [("kept",kept),("ambiguous_window",dropped)]]
    return (dataset=dataset, source_ids=sources, audit=audit)
end

splice_transactions(path::AbstractString; positions=DNA_POSITIONS)::PreparedDataset =
    prepare_splice(path; positions=positions).dataset

"""Compare supplied frequent candidates without invoking a mining implementation.

Counts are recomputed on every class, including candidates absent from that class's
frequent output. This function is testable while A's miner is awaiting approval.
"""
function compare_dna_patterns(dataset::PreparedDataset,
                             patterns_by_class::AbstractDict{String,Vector{Pattern}})::Vector{DNAPatternComparison}
    dataset.classes !== nothing || throw(ArgumentError("DNA class metadata is required"))
    dataset.dataset_id == "splice" || throw(ArgumentError("Expected a splice dataset"))
    Set(keys(patterns_by_class)) == Set(DNA_CLASSES) ||
        throw(ArgumentError("patterns_by_class must contain EI, IE and N"))
    dataset.item_labels == dna_item_labels() || throw(ArgumentError("DNA mapping must match the frozen 48 position/base IDs"))
    all(t -> length(t)==12 && all(id -> 1<=id<=48,t) && allunique(fld(id-1,4) for id in t),dataset.transactions) ||
        throw(ArgumentError("Each DNA observation must contain one base per frozen position"))
    indices = Dict(label => findall(==(label), dataset.classes) for label in DNA_CLASSES)
    all(label -> !isempty(indices[label]), DNA_CLASSES) || throw(ArgumentError("An empty DNA class cannot be compared"))
    candidates = Set{Itemset}()
    declared = Dict{Tuple{String,Itemset},Int}()
    for label in DNA_CLASSES, pattern in patterns_by_class[label]
        pattern.support <= length(indices[label]) || throw(ArgumentError("Pattern support exceeds class size"))
        all(id -> 1 <= id <= 48, pattern.items) &&
            allunique(fld(id-1,4) for id in pattern.items) ||
            throw(ArgumentError("Invalid position/base pattern"))
        haskey(declared,(label,pattern.items)) && throw(ArgumentError("Duplicate pattern in a class"))
        declared[(label,pattern.items)] = pattern.support
        2 <= length(pattern.items) <= 4 && push!(candidates, pattern.items)
    end
    result = DNAPatternComparison[]
    for key in candidates
        counts = [count(i -> all(item -> item in dataset.transactions[i], key), indices[label]) for label in DNA_CLASSES]
        for (i,label) in enumerate(DNA_CLASSES)
            haskey(declared,(label,key)) && declared[(label,key)] != counts[i] &&
                throw(ArgumentError("Declared support differs from observations for $label / $key"))
        end
        sizes = [length(indices[label]) for label in DNA_CLASSES]
        push!(result, DNAPatternComparison(key, counts..., sizes...))
    end
    sort!(result; by=p -> (-p.support_span,-max(p.support_EI,p.support_IE,p.support_N),length(p.items),p.items))
    return result
end

function write_dna_comparisons(path::AbstractString, dataset::PreparedDataset, comparisons::Vector{DNAPatternComparison})
    header = ("rank","pattern_ids","pattern_labels","length","count_EI","count_IE","count_N",
              "n_EI","n_IE","n_N","support_EI","support_IE","support_N","support_span")
    ordered = sort(comparisons; by=p -> (-p.support_span,-max(p.support_EI,p.support_IE,p.support_N),length(p.items),p.items))
    rows = ((i,join(p.items,' '),join((dataset.item_labels[id] for id in p.items)," | "),length(p.items),
             p.count_EI,p.count_IE,p.count_N,p.n_EI,p.n_IE,p.n_N,p.support_EI,p.support_IE,p.support_N,p.support_span)
            for (i,p) in enumerate(ordered))
    return write_csv_table(path,header,rows)
end
