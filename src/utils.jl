"""Read numeric SPMF transactions. Ignore blank and #/%/@ metadata lines.

Reject unsorted/duplicate items so preprocessing choices are explicit.
Identical transaction rows are retained: each is a different TID.
"""
function read_transactions(path::AbstractString)::Vector{Vector{Int}}
    transactions = Vector{Int}[]
    open(path, "r") do io
        for (number, raw) in enumerate(eachline(io))
            line = strip(raw)
            (isempty(line) || startswith(line, r"^[#%@]")) && continue
            items = try
                parse.(Int, split(line))
            catch
                throw(ArgumentError("$path:$number: expected integer item IDs"))
            end
            all(>(0), items) || throw(ArgumentError("$path:$number: IDs must be positive"))
            issorted(items) && allunique(items) ||
                throw(ArgumentError("$path:$number: sort and deduplicate items first"))
            push!(transactions, items)
        end
    end
    return transactions
end

"""Parse exact decimal relative support (0.4 or 40%); no float rounding."""
function parse_minsup(raw::AbstractString)::Rational{BigInt}
    value = strip(raw)
    percent = endswith(value, "%")
    percent && (value = chop(value))
    occursin(r"^\d+(\.\d+)?$", value) ||
        throw(ArgumentError("minsup must be a decimal fraction or percentage"))
    parts = split(value, '.')
    fraction = length(parts) == 2 ? parts[2] : ""
    numerator = parse(BigInt, parts[1] * fraction)
    denominator = big(10)^length(fraction) * (percent ? 100 : 1)
    support = numerator // denominator
    0 < support <= 1 || throw(ArgumentError("minsup must lie in (0, 1]"))
    return support
end

function minimum_count(relative::Rational, n::Integer)::Int
    n >= 0 || throw(ArgumentError("Transaction count cannot be negative"))
    0 < relative <= 1 || throw(ArgumentError("minsup must lie in (0, 1]"))
    return max(1, ceil(Int, relative * n))
end

function write_patterns(path::AbstractString, patterns)
    ordered = sort!(collect(patterns); by=p -> (length(p.items), p.items))
    allunique(p.items for p in ordered) || throw(ArgumentError("Duplicate itemsets"))
    mkpath(dirname(abspath(path)))
    open(path, "w") do io
        for p in ordered
            println(io, join(p.items, ' '), " #SUP: ", p.support)
        end
    end
    return path
end

"""Canonical SPMF output map, independent of line/item order; reject duplicates."""
function read_patterns(path::AbstractString)::Dict{Itemset,Int}
    result = Dict{Itemset,Int}()
    open(path, "r") do io
        for (number, raw) in enumerate(eachline(io))
            line = strip(raw)
            (isempty(line) || startswith(line, r"^[#%@]")) && continue
            parts = split(line, "#SUP:")
            length(parts) == 2 || throw(ArgumentError("$path:$number: invalid output"))
            pattern = Pattern(parse.(Int, split(strip(parts[1]))), parse(Int, strip(parts[2])))
            haskey(result, pattern.items) && throw(ArgumentError("Duplicate output itemset"))
            result[pattern.items] = pattern.support
        end
    end
    return result
end

function mine(transactions::Vector{Vector{Int}}, min_count::Integer;
              backend::Symbol=:list)::Vector{Pattern}
    min_count >= 1 || throw(ArgumentError("Absolute minimum support must be >= 1"))
    for items in transactions
        all(>(0), items) && issorted(items) && allunique(items) ||
            throw(ArgumentError("Transactions must contain sorted unique positive IDs"))
    end
    engine = backend == :list ? ListBackend() :
             backend == :bitset ? BitsetBackend() :
             throw(ArgumentError("backend must be list or bitset"))
    isempty(transactions) && return Pattern[]
    min_count > length(transactions) && return Pattern[]
    return mine(engine, transactions, Int(min_count))
end
