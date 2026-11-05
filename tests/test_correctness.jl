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
