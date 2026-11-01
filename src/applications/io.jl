"""Strict RFC 4180 reader. Return physical start line and string fields per record.

Preserves quoted commas/newlines/escaped quotes; skips physically empty lines.
Malformed quoting fails rather than silently shifting a basket or sequence.
"""
function csv_records(path::AbstractString)
    chars = collect(read(path, String))
    !isempty(chars) && first(chars) == '\ufeff' && popfirst!(chars)
    records = Tuple{Int,Vector{String}}[]
    fields = String[]
    buffer = IOBuffer()
    state, active = :start, false
    line, start, i = 1, 1, 1
    while i <= length(chars)
        c = chars[i]
        if state == :quoted
            if c == '"'
                if i < length(chars) && chars[i+1] == '"'
                    print(buffer, '"'); i += 1
                else
                    state = :closed
                end
            else
                print(buffer, c)
                (c == '\n' || (c == '\r' && (i == length(chars) || chars[i+1] != '\n'))) && (line += 1)
            end
        elseif c == ','
            push!(fields, String(take!(buffer)))
            state, active = :start, true
        elseif c == '\r' || c == '\n'
            if active
                push!(fields, String(take!(buffer)))
                push!(records, (start, fields))
                fields = String[]
            end
            c == '\r' && i < length(chars) && chars[i+1] == '\n' && (i += 1)
            line += 1; start = line
            state, active = :start, false
        elseif state == :closed
            throw(ArgumentError("$path:$line: unexpected character after closing CSV quote"))
        elseif c == '"'
            state == :start || throw(ArgumentError("$path:$line: quote in an unquoted field"))
            state, active = :quoted, true
        else
            print(buffer, c)
            state, active = :bare, true
        end
        i += 1
    end
    state == :quoted && throw(ArgumentError("$path:$start: unterminated CSV quote"))
    if active
        push!(fields, String(take!(buffer)))
        push!(records, (start, fields))
    end
    return records
end

function write_csv_table(path::AbstractString, header, rows)
    mkpath(dirname(abspath(path)))
    open(path, "w") do io
        for row in Iterators.flatten(((header,), rows))
            length(row) == length(header) || throw(ArgumentError("CSV row/header width mismatch"))
            println(io, join(('"' * replace(string(value), "\"" => "\"\"") * '"' for value in row), ','))
        end
    end
    return path
end

"""Export one prepared application dataset into a new or empty directory."""
function write_prepared_dataset(dataset::PreparedDataset, directory::AbstractString;
                                source_ids=dataset.row_ids, audit=Tuple[])
    length(source_ids) == length(dataset.transactions) || throw(ArgumentError("source_ids length mismatch"))
    isdir(directory) && !isempty(readdir(directory)) &&
        throw(ArgumentError("Prepared output directory must be empty; choose a new destination"))
    mkpath(directory)
    open(joinpath(directory, "transactions.txt"), "w") do io
        for transaction in dataset.transactions
            println(io, join(transaction, ' '))
        end
    end
    item_rows = []
    for id in sort!(collect(keys(dataset.item_labels)))
        label = dataset.item_labels[id]
        token = dataset.dataset_id == "splice" ? match(r"^pos=([+-]?\d+);base=([ACGT])$", label) : nothing
        push!(item_rows, (id, label, token === nothing ? "" : token[1], token === nothing ? "" : token[2]))
    end
    write_csv_table(joinpath(directory, "items.csv"), ("item_id","item_label","position","base"), item_rows)
    write_csv_table(joinpath(directory, "observations.csv"), ("tid","row_id","source_id","class"),
        ((i,dataset.row_ids[i],source_ids[i],dataset.classes === nothing ? "" : dataset.classes[i])
         for i in eachindex(dataset.transactions)))
    write_csv_table(joinpath(directory, "preparation_audit.csv"),
        ("schema_version","dataset_id","class","reason","count"), audit)
    return directory
end
