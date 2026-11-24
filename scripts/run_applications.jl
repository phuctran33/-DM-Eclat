using EclatProject
using TOML
using SHA

const APPLICATION_ROOT = dirname(@__DIR__)
file_hash(path) = bytes2hex(open(sha256, path))

function run_groceries(config, input, staging)
    prepared = prepare_groceries(input)
    data = prepared.dataset
    result = groceries_application(data; minsup=config["minsup"], minconf=config["minconf"], top_k=config["top_k"])
    write_prepared_dataset(data, joinpath(staging, "prepared", "groceries");
        source_ids=prepared.source_ids, audit=prepared.audit)
    write_patterns(joinpath(staging, "patterns", "groceries.txt"), result.patterns)
    write_association_rules(joinpath(staging, "groceries_rules.csv"), data, result.rules)
    write_association_rules(joinpath(staging, "groceries_top10.csv"), data, result.rules; top_k=config["top_k"])
    println("Groceries: $(length(result.patterns)) frequent patterns, $(length(result.rules)) rules, min_count=$(result.min_count)")
    return Dict("n_transactions"=>length(data.transactions), "n_items"=>length(data.item_labels),
        "min_count"=>result.min_count, "n_patterns"=>length(result.patterns),
        "n_rules"=>length(result.rules), "n_top_rules"=>length(result.top10))
end

function run_splice(config, input, staging)
    config["positions_1based"] == collect(DNA_POSITIONS) && config["classes"] == collect(DNA_CLASSES) &&
        config["base_order"] == string.(collect(DNA_BASE_ORDER)) &&
        config["display_pattern_lengths"] == [2,3,4] && config["label_is_mined_item"] == false ||
        throw(ArgumentError("DNA config must preserve schema v1"))
    prepared = prepare_splice(input)
    data = prepared.dataset
    result = dna_application(data; minsup=config["minsup"])
    directory = joinpath(staging, "prepared", "splice")
    write_prepared_dataset(data, directory; source_ids=prepared.source_ids, audit=prepared.audit)
    classes = Dict{String,Dict{String,Int}}()
    for label in DNA_CLASSES
        patterns = result.patterns_by_class[label]
        write_patterns(joinpath(staging, "patterns", "splice_$label.txt"), patterns)
        indices = findall(==(label), data.classes)
        open(joinpath(directory, "transactions_$label.txt"), "w") do io
            for i in indices
                println(io, join(data.transactions[i], ' '))
            end
        end
        classes[label] = Dict("n_transactions"=>length(indices),
            "min_count"=>result.min_counts[label], "n_patterns"=>length(patterns))
        println("Splice $label: $(length(patterns)) patterns, min_count=$(result.min_counts[label])")
    end
    write_dna_comparisons(joinpath(staging, "dna_patterns.csv"), data, result.comparisons)
    println("DNA comparisons: $(length(result.comparisons))")
    return Dict("n_transactions"=>length(data.transactions), "n_items"=>length(data.item_labels),
        "n_comparisons"=>length(result.comparisons), "classes"=>classes)
end

function run_applications(config_path::AbstractString, output::AbstractString; root=APPLICATION_ROOT, dataset="all")
    dataset in ("all", "groceries", "splice") || throw(ArgumentError("Choose all, groceries or splice"))
    destination = abspath(output)
    (ispath(destination) && (!isdir(destination) || !isempty(readdir(destination)))) &&
        throw(ArgumentError("Output must be new or empty; existing results are preserved"))
    config = TOML.parsefile(config_path)
    config["schema_version"] == SCHEMA_VERSION || throw(ArgumentError("Unsupported schema version"))
    sources, statistics = Dict{String,String}(), Dict{String,Any}()
    mkpath(dirname(destination))
    staging = mktempdir(dirname(destination); prefix=".applications-")
    promoted = false
    try
        if dataset in ("all", "groceries")
            input = abspath(root, config["groceries"]["input"])
            sources["groceries"] = file_hash(input)
            statistics["groceries"] = run_groceries(config["groceries"], input, staging)
        end
        if dataset in ("all", "splice")
            input = abspath(root, config["dna"]["input"])
            sources["splice"] = file_hash(input)
            statistics["dna"] = run_splice(config["dna"], input, staging)
        end
        hashes = Dict{String,String}()
        for (folder, _, files) in walkdir(staging), name in files
            path = joinpath(folder, name)
            hashes[replace(relpath(path, staging), '\\'=>'/')] = file_hash(path)
        end
        code_hashes = Dict{String,String}()
        for directory in ("src", "scripts")
            for (folder, _, files) in walkdir(joinpath(APPLICATION_ROOT, directory)), name in files
                endswith(name, ".jl") || continue
                path = joinpath(folder, name)
                code_hashes[replace(relpath(path, APPLICATION_ROOT), '\\'=>'/')] = file_hash(path)
            end
        end
        metadata = Dict("schema_version"=>SCHEMA_VERSION, "seed"=>config["seed"], "julia_version"=>string(VERSION),
            "config"=>config, "config_sha256"=>file_hash(config_path), "input_sha256"=>sources,
            "source_sha256"=>code_hashes, "artifact_sha256"=>hashes, "statistics"=>statistics,
            "backend_verification"=>"complete itemset/support maps: list == bitset",
            "pattern_policy"=>"mine complete outputs; filter DNA lengths 2-4 only for comparison",
            "result_kind"=>"mined by group Eclat, not manually supplied candidates")
        open(joinpath(staging, "run.toml"), "w") do io
            TOML.print(io, metadata; sorted=true)
        end
        # Promote only a complete run and recheck the destination before moving it.
        if ispath(destination)
            isdir(destination) && isempty(readdir(destination)) || error("Output changed during run; preserved existing contents")
            rm(destination)
        end
        mv(staging, destination)
        promoted = true
        println("Applications output: $destination")
        return metadata
    finally
        !promoted && isdir(staging) && rm(staging; recursive=true)
    end
end

function main(args)
    config = joinpath(APPLICATION_ROOT, "configs", "applications.toml")
    output = joinpath(APPLICATION_ROOT, "results", "applications")
    dataset = "all"
    length(args) % 2 == 0 || throw(ArgumentError("Usage: run_applications.jl [--dataset all|groceries|splice] [--config FILE] [--output NEW_DIRECTORY]"))
    for i in 1:2:length(args)
        if args[i] == "--config"
            config = abspath(args[i+1])
        elseif args[i] == "--output"
            output = abspath(args[i+1])
        elseif args[i] == "--dataset"
            dataset = args[i+1]
        else
            throw(ArgumentError("Unknown option $(args[i])"))
        end
    end
    run_applications(config, output; dataset)
end

if abspath(PROGRAM_FILE) == @__FILE__
    try
        main(ARGS)
    catch error
        showerror(stderr, error)
        println(stderr)
        exit(1)
    end
end
