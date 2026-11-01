"""Read canonical basket_id,item_name CSV and apply schema v1.0.0."""
function prepare_groceries(path::AbstractString)
    records = csv_records(path)
    !isempty(records) && records[1][2] == ["basket_id","item_name"] ||
        throw(ArgumentError("Groceries CSV requires header basket_id,item_name"))
    baskets = Dict{String,Set{String}}()
    duplicates = 0
    for (line, fields) in records[2:end]
        length(fields) == 2 || throw(ArgumentError("$path:$line: expected 2 CSV fields"))
        id = strip(fields[1])
        name = replace(strip(lowercase(Unicode.normalize(fields[2], :NFC))), r"\s+" => " ")
        isempty(id) && throw(ArgumentError("$path:$line: empty basket_id"))
        isempty(name) && throw(ArgumentError("$path:$line: empty item_name"))
        basket = get!(() -> Set{String}(), baskets, id)
        name in basket && (duplicates += 1)
        push!(basket, name)
    end
    isempty(baskets) && throw(ArgumentError("Groceries contains no baskets"))
    vocabulary = sort!(unique([name for basket in values(baskets) for name in basket]))
    mapping = Dict(id => name for (id,name) in enumerate(vocabulary))
    reverse_mapping = Dict(name => id for (id,name) in mapping)
    row_ids = sort!(collect(keys(baskets)))
    transactions = [sort!([reverse_mapping[name] for name in baskets[id]]) for id in row_ids]
    dataset = PreparedDataset("groceries", transactions, mapping, row_ids)
    audit = [(SCHEMA_VERSION,"groceries","ALL","kept",length(row_ids)),
             (SCHEMA_VERSION,"groceries","ALL","duplicate_item_rows_collapsed",duplicates)]
    return (dataset=dataset, source_ids=copy(row_ids), audit=audit)
end

groceries_transactions(path::AbstractString)::PreparedDataset = prepare_groceries(path).dataset
