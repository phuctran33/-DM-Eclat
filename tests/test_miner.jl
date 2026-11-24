using SHA

# Independent exhaustive oracle ONLY for tiny test databases, never benchmarks.
function brute_force(transactions, min_count)
    universe = sort!(unique(vcat(transactions...)))
    length(universe) <= 12 || error("Oracle is restricted to small inputs")
    result = Dict{Itemset,Int}()
    for mask in 1:((1 << length(universe)) - 1)
        key = Tuple(universe[i] for i in eachindex(universe) if (mask & (1 << (i - 1))) != 0)
        support = count(t -> all(x -> x in t, key), transactions)
        support >= min_count && (result[key] = support)
    end
    return result
end

@testset "Edge cases, input ownership and packed-word boundaries" begin
    cases = [Vector{Int}[], [Int[]], [[91]], [[1, 1001], [1, 1001]],
             [Int[], [2, 900], [900]], [collect(1:8) for _ in 1:3]]
    rng = MersenneTwister(123)
    append!(cases, [[findall(rand(rng, 5) .< 0.6) for _ in 1:n]
                    for n in [63, 64, 65, 127, 128, 129]])
    for transactions in cases
        before = deepcopy(transactions)
        for threshold in unique([1, max(1, length(transactions)), length(transactions) + 1])
            expected = isempty(transactions) ? Dict{Itemset,Int}() : brute_force(transactions, threshold)
            for backend in TEST_BACKENDS
                patterns = mine(transactions, threshold; backend=backend)
                @test Dict(p.items => p.support for p in patterns) == expected
                @test length(patterns) == length(expected)
                @test all(p -> issorted(p.items) && !isempty(p.items), patterns)
                @test transactions == before
            end
        end
    end
    for backend in TEST_BACKENDS
        for invalid in [[[2, 1]], [[1, 1]], [[0]], [[-2]]]
            @test_throws ArgumentError mine(invalid, 1; backend=backend)
        end
    end
    for (a, b) in [(Int[], [1]), ([1, 3, 7], [2, 3, 7, 8]), ([1], Int[])]
        @test EclatProject.intersect_tids(a, b) == sort!(intersect(a, b))
    end
end

@testset "Eclat: five different databases, selected backends" begin
    fixtures = ["basic", "dense", "sparse", "duplicates", "boundary"]
    for name in fixtures
        transactions = read_transactions(joinpath(@__DIR__, "..", "data", "toy", "$name.txt"))
        for threshold in unique([1, 2, length(transactions), length(transactions) + 1])
            expected = brute_force(transactions, threshold)
            for backend in TEST_BACKENDS
                patterns = mine(transactions, threshold; backend=backend)
                actual = Dict(p.items => p.support for p in patterns)
                @test length(actual) == length(patterns)
                @test actual == expected
            end
        end
    end
end

@testset "Randomized oracle and transaction-order invariance" begin
    rng = MersenneTwister(42)
    for _ in 1:20
        transactions = [findall(rand(rng, 7) .< 0.4) for _ in 1:12]
        threshold = rand(rng, 1:12)
        expected = brute_force(transactions, threshold)
        for backend in TEST_BACKENDS
            @test Dict(p.items => p.support for p in mine(transactions, threshold; backend=backend)) == expected
            @test Dict(p.items => p.support for p in mine(reverse(transactions), threshold; backend=backend)) == expected
        end
    end
end

@testset "B: independently generated SPMF references and provenance" begin
    # Expected toy support maps at 40%, kept separately from Java SPMF outputs.
    expected = Dict(
        "basic" => Dict{Itemset,Int}(
            (1,) => 4, (2,) => 4, (3,) => 4, (1, 2) => 3,
            (1, 3) => 3, (2, 3) => 3, (1, 2, 3) => 2,
        ),
        "boundary" => Dict{Itemset,Int}(
            (1,) => 2, (2,) => 2, (3,) => 2, (4,) => 2,
        ),
        "dense" => Dict{Itemset,Int}(
            (1,) => 5, (2,) => 5, (3,) => 5, (4,) => 5,
            (1, 2) => 4, (1, 3) => 4, (1, 4) => 4, (2, 3) => 4,
            (2, 4) => 4, (3, 4) => 4, (1, 2, 3) => 3, (1, 2, 4) => 3,
            (1, 3, 4) => 3, (2, 3, 4) => 3,
        ),
        "duplicates" => Dict{Itemset,Int}(
            (1,) => 3, (2,) => 5, (3,) => 2, (1, 2) => 3,
            (2, 3) => 2,
        ),
        "sparse" => Dict{Itemset,Int}(),
    )
    root=dirname(@__DIR__)
    records=EclatProject.csv_records(joinpath(root,"tests/reference/spmf/manifest.csv"))
    expected_header=["schema_version","dataset","input_path","input_sha256","minsup","min_count","n_transactions","output_path","output_sha256","spmf_version","spmf_jar_sha256","java_version","command","status"]
    @test records[1][2]==expected_header
    @test length(records)==6
    fields=Dict(key=>i for (i,key) in enumerate(records[1][2]))
    @test Set(row[2][fields["dataset"]] for row in records[2:end])==Set(["basic","dense","sparse","duplicates","boundary"])
    for (_,row) in records[2:end]
        name=row[fields["dataset"]]
        input=joinpath(root,"data/toy/$name.txt")
        output=joinpath(root,"tests/reference/spmf/$name.txt")
        transactions=read_transactions(input)
        @test row[fields["schema_version"]]=="1.0.0"
        @test row[fields["status"]]=="ok"
        @test row[fields["minsup"]]=="0.4"
        @test parse(Int,row[fields["min_count"]])==minimum_count(parse_minsup("40%"),length(transactions))
        @test parse(Int,row[fields["n_transactions"]])==length(transactions)
        @test row[fields["input_sha256"]]==bytes2hex(open(sha256,input))
        @test row[fields["output_sha256"]]==bytes2hex(open(sha256,output))
        @test row[fields["spmf_jar_sha256"]]=="c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"
        @test row[fields["spmf_version"]]=="2.64b"
        @test !occursin('\r',read(output,String)) # Git checkout must preserve the declared output hash
        @test read_patterns(output) == expected[name]
        @test occursin("run Eclat",row[fields["command"]])
        @test endswith(row[fields["command"]],"40%")
    end
end

# References must be freshly produced by Java SPMF; handwritten output is not a reference run.
@testset "Exact agreement with SPMF on five databases" begin
    for name in ["basic", "dense", "sparse", "duplicates", "boundary"]
        input = joinpath(@__DIR__, "..", "data", "toy", "$name.txt")
        reference_path = joinpath(@__DIR__, "reference", "spmf", "$name.txt")
        @test isfile(reference_path)
        if isfile(reference_path)
            reference = read_patterns(reference_path)
            transactions = read_transactions(input)
            threshold = minimum_count(parse_minsup("40%"), length(transactions))
            for backend in TEST_BACKENDS
                patterns = mine(transactions, threshold; backend=backend)
                @test length(patterns) == length(reference)
                @test Dict(p.items => p.support for p in patterns) == reference
            end
        end
    end
end
