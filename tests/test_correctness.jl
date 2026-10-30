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
