using EclatProject
using TOML
using SHA

const APPLICATION_ROOT = dirname(@__DIR__)
file_hash(path) = bytes2hex(open(sha256, path))

function run_applications(config_path::AbstractString, output::AbstractString; root=APPLICATION_ROOT)
    destination = abspath(output)
    (ispath(destination) && (!isdir(destination) || !isempty(readdir(destination)))) &&
        throw(ArgumentError("Output must be new or empty; existing results are preserved"))
    config = TOML.parsefile(config_path)
    config["schema_version"] == SCHEMA_VERSION || throw(ArgumentError("Unsupported schema version"))
    g, d = config["groceries"], config["dna"]
    d["positions_1based"] == collect(DNA_POSITIONS) && d["classes"] == collect(DNA_CLASSES) &&
        d["base_order"] == string.(collect(DNA_BASE_ORDER)) &&
        d["display_pattern_lengths"] == [2,3,4] && d["label_is_mined_item"] == false ||
        throw(ArgumentError("DNA config must preserve frozen schema v1"))
    inputs = Dict("groceries" => abspath(root,g["input"]), "splice" => abspath(root,d["input"]))
    sources = Dict(name => file_hash(path) for (name,path) in inputs)
    groceries, splice = prepare_groceries(inputs["groceries"]), prepare_splice(inputs["splice"])
    gr = groceries_application(groceries.dataset; minsup=g["minsup"], minconf=g["minconf"], top_k=g["top_k"])
    dna = dna_application(splice.dataset; minsup=d["minsup"])
    # Compute and validate before writing; promote a complete staged directory only.
    mkpath(dirname(destination))
    staging = mktempdir(dirname(destination); prefix=".applications-")
    promoted = false
    try
        write_prepared_dataset(groceries.dataset,joinpath(staging,"prepared","groceries"); source_ids=groceries.source_ids,audit=groceries.audit)
        write_prepared_dataset(splice.dataset,joinpath(staging,"prepared","splice"); source_ids=splice.source_ids,audit=splice.audit)
        write_patterns(joinpath(staging,"patterns","groceries.txt"),gr.patterns)
        for label in DNA_CLASSES
            write_patterns(joinpath(staging,"patterns","splice_$label.txt"),dna.patterns_by_class[label])
            indices=findall(==(label),splice.dataset.classes)
            open(joinpath(staging,"prepared","splice","transactions_$label.txt"),"w") do io
                for i in indices
                    println(io,join(splice.dataset.transactions[i],' '))
                end
            end
        end
        write_association_rules(joinpath(staging,"groceries_rules.csv"),groceries.dataset,gr.rules)
        write_association_rules(joinpath(staging,"groceries_top10.csv"),groceries.dataset,gr.rules; top_k=g["top_k"])
        write_dna_comparisons(joinpath(staging,"dna_patterns.csv"),splice.dataset,dna.comparisons)
        statistics = Dict("groceries" => Dict("n_transactions"=>length(groceries.dataset.transactions),
            "n_items"=>length(groceries.dataset.item_labels),"min_count"=>gr.min_count,"n_patterns"=>length(gr.patterns),
            "n_rules"=>length(gr.rules),"n_top_rules"=>length(gr.top10)),
            "dna"=>Dict("n_transactions"=>length(splice.dataset.transactions),"n_items"=>48,
            "n_comparisons"=>length(dna.comparisons),
            "classes"=>Dict(label=>Dict("n_transactions"=>count(==(label),splice.dataset.classes),
                "min_count"=>dna.min_counts[label],"n_patterns"=>length(dna.patterns_by_class[label])) for label in DNA_CLASSES)))
        hashes=Dict()
        for (directory,_,files) in walkdir(staging), name in files
            path=joinpath(directory,name)
            hashes[replace(relpath(path,staging),'\\'=>'/')] = file_hash(path)
        end
        code_hashes=Dict()
        for directory in [joinpath(root,"src"),joinpath(root,"scripts")]
            for (folder,_,files) in walkdir(directory), name in files
                endswith(name,".jl") || continue
                path=joinpath(folder,name)
                code_hashes[replace(relpath(path,root),'\\'=>'/')] = file_hash(path)
            end
        end
        metadata=Dict("schema_version"=>SCHEMA_VERSION,"seed"=>config["seed"],"julia_version"=>string(VERSION),
            "config"=>config,"config_sha256"=>file_hash(config_path),"input_sha256"=>sources,
            "source_sha256"=>code_hashes,"artifact_sha256"=>hashes,"statistics"=>statistics,
            "backend_verification"=>"complete itemset/support maps: list == bitset",
            "pattern_policy"=>"mine complete outputs; filter DNA lengths 2-4 only for comparison",
            "result_kind"=>"mined by group Eclat, not manually supplied candidates")
        open(joinpath(staging,"run.toml"),"w") do io
            TOML.print(io,metadata; sorted=true)
        end
        # Recheck ownership immediately before promotion.
        if ispath(destination)
            isdir(destination) && isempty(readdir(destination)) || error("Output changed during run; preserved existing contents")
            rm(destination) # empty directory only
        end
        mv(staging,destination)
        promoted=true
        println("Groceries: $(length(gr.patterns)) frequent patterns, $(length(gr.rules)) rules, $(length(gr.top10)) top rules; min_count=$(gr.min_count)")
        for label in DNA_CLASSES
            println("Splice $label: $(length(dna.patterns_by_class[label])) patterns; min_count=$(dna.min_counts[label])")
        end
        println("DNA comparisons: $(length(dna.comparisons)); output=$destination")
        return metadata
    finally
        !promoted && isdir(staging) && rm(staging; recursive=true)
    end
end

function main(args)
    config=joinpath(APPLICATION_ROOT,"configs","applications.toml")
    output=joinpath(APPLICATION_ROOT,"results","applications")
    length(args)%2==0 || throw(ArgumentError("Usage: run_applications.jl [--config FILE] [--output NEW_DIRECTORY]"))
    for i in 1:2:length(args)
        if args[i]=="--config"
            config=abspath(args[i+1])
        elseif args[i]=="--output"
            output=abspath(args[i+1])
        else
            throw(ArgumentError("Unknown option $(args[i])"))
        end
    end
    run_applications(config,output)
end

if abspath(PROGRAM_FILE)==@__FILE__
    try
        main(ARGS)
    catch err
        showerror(stderr,err);println(stderr);exit(1)
    end
end
