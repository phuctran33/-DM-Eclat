using EclatProject
using SHA

# Internal timer includes read + validation + verticalization + mining.
# Batch mode warms the complete case once, then repeats in the same runtime.
function main(args)
    batch = !isempty(args) && first(args) == "--batch"
    batch && (args = args[2:end])
    length(args) == 5 || error("Usage: benchmark_worker.jl INPUT MINSUP BACKEND REPEAT OUTPUT.txt")
    input, minsup, backend_name, repeat, output = args
    relative = parse_minsup(minsup)
    backend = Symbol(backend_name)
    input_hash = bytes2hex(open(sha256, input))
    run_id = string(time_ns(), '-', getpid())
    # Compile common code, then warm the actual case (including tuple lengths).
    mine([[1, 2], [1], [2]], 1; backend=backend)
    warm_transactions = read_transactions(input)
    expected = Dict(p.items => p.support for p in
        mine(warm_transactions, minimum_count(relative, length(warm_transactions)); backend=backend))
    warm_transactions = nothing
    println("schema_version,run_id,dataset,input_sha256,backend,minsup,min_count,repeat,seed,n_transactions,n_patterns,metric_scope,seconds,allocated_bytes,peak_rss_mib,status,julia_version,java_version,spmf_version")
    repetitions = batch ? (1:parse(Int, repeat)) : (parse(Int, repeat):parse(Int, repeat))
    for repetition in repetitions
        GC.gc()
        threshold = Ref(0)
        transaction_count = Ref(0)
        run = @timed begin
            transactions = read_transactions(input)
            transaction_count[] = length(transactions)
            threshold[] = minimum_count(relative, transaction_count[])
            mine(transactions, threshold[]; backend=backend)
        end
        Dict(p.items => p.support for p in run.value) == expected || error("Repetition changed output")
        write_patterns(output, run.value) # serialization and verification outside timer
        fields = (SCHEMA_VERSION, "$run_id-$repetition", splitext(basename(input))[1], input_hash,
                  backend_name, Float64(relative), threshold[], repetition, 42,
                  transaction_count[], length(run.value), "internal_read_mine",
                  run.time, run.bytes, "NA", "ok", VERSION, "NA", "NA")
        println(join(("\"" * replace(string(field), "\"" => "\"\"") * "\"" for field in fields), ','))
        flush(stdout)
    end
end

main(ARGS)
