using EclatProject

const HELP = """
Eclat project template (algorithm implementation pending)
Usage:
  julia --project=. scripts/mine.jl --input FILE --output FILE --minsup 0.4 [--backend list|bitset]
  julia --project=. scripts/mine.jl --input FILE --output FILE --min-count 2 [--backend list|bitset]
Accepts relative decimals or percentages, e.g. 0.4 or 40%.
Exactly one of --minsup / --min-count is required.
"""

function main(args)
    if isempty(args) || args == ["--help"] || args == ["-h"]
        println(HELP)
        return
    end
    iseven(length(args)) || throw(ArgumentError(HELP))
    options = Dict{String,String}()
    allowed = Set(["--input", "--output", "--minsup", "--min-count", "--backend"])
    for i in 1:2:length(args)
        key = args[i]
        key in allowed || throw(ArgumentError("Unknown option $key"))
        haskey(options, key) && throw(ArgumentError("Duplicate option $key"))
        options[key] = args[i + 1]
    end
    all(k -> haskey(options, k), ["--input", "--output"]) || throw(ArgumentError(HELP))
    xor(haskey(options, "--minsup"), haskey(options, "--min-count")) ||
        throw(ArgumentError("Specify exactly one support option"))
    abspath(options["--input"]) == abspath(options["--output"]) &&
        throw(ArgumentError("Output must differ from input"))
    transactions = read_transactions(options["--input"])
    threshold = haskey(options, "--minsup") ?
        minimum_count(parse_minsup(options["--minsup"]), length(transactions)) :
        parse(Int, options["--min-count"])
    patterns = mine(transactions, threshold; backend=Symbol(get(options, "--backend", "list")))
    write_patterns(options["--output"], patterns)
    println("transactions=$(length(transactions)), min_count=$threshold, patterns=$(length(patterns))")
end

try
    main(ARGS)
catch err
    showerror(stderr, err)
    println(stderr)
    exit(1)
end
