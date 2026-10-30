using EclatProject

# One process per dataset/backend/support/repeat. External monitor measures RSS.
# Deliberately fails on the current TODO core instead of fabricating results.
function main(args)
    length(args) == 5 || error("Usage: benchmark_worker.jl INPUT MINSUP BACKEND REPEAT OUTPUT.txt")
    input, minsup, backend_name, repeat, output = args
    relative = parse_minsup(minsup)
    backend = Symbol(backend_name)
    # Compile on a tiny database before measuring. No full dataset is retained here.
    mine([[1, 2], [1], [2]], 1; backend=backend)
    GC.gc()
    threshold = Ref(0)
    transaction_count = Ref(0)
    run = @timed begin
        transactions = read_transactions(input)
        transaction_count[] = length(transactions)
        threshold[] = minimum_count(relative, transaction_count[])
        mine(transactions, threshold[]; backend=backend)
    end
    write_patterns(output, run.value) # output serialization is outside internal timer
    println("input,minsup,backend,repeat,n_transactions,min_count,n_patterns,read_and_mine_seconds,allocated_bytes,peak_rss_mib")
    escaped_input = "\"" * replace(input, "\"" => "\"\"") * "\""
    println(join((escaped_input, minsup, backend_name, repeat, transaction_count[], threshold[],
                  length(run.value), run.time, run.bytes, "NA"), ','))
    println(stderr, "RSS is NOT measured here. Use an external process monitor; allocations are not peak memory.")
end

main(ARGS)
