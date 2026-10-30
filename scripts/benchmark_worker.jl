using EclatProject
using SHA

# One process per dataset/backend/support/repeat. External monitor measures RSS.
# Deliberately fails on the current TODO core instead of fabricating results.
function main(args)
    length(args) == 5 || error("Usage: benchmark_worker.jl INPUT MINSUP BACKEND REPEAT OUTPUT.txt")
    input, minsup, backend_name, repeat, output = args
    relative = parse_minsup(minsup)
    backend = Symbol(backend_name)
    input_hash = bytes2hex(open(sha256, input))
    run_id = string(time_ns(), '-', getpid())
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
    println("schema_version,run_id,dataset,input_sha256,backend,minsup,min_count,repeat,seed,n_transactions,n_patterns,metric_scope,seconds,allocated_bytes,peak_rss_mib,status,julia_version,java_version,spmf_version")
    fields = (SCHEMA_VERSION, run_id, splitext(basename(input))[1], input_hash,
              backend_name, Float64(relative), threshold[], repeat, 42,
              transaction_count[], length(run.value), "internal_read_mine",
              run.time, run.bytes, "NA", "ok", VERSION, "NA", "NA")
    println(join(("\"" * replace(string(field), "\"" => "\"\"") * "\"" for field in fields), ','))
    println(stderr, "RSS is NOT measured here. Use an external process monitor; allocations are not peak memory.")
end

main(ARGS)
