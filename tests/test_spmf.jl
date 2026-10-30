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
