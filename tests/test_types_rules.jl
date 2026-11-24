@testset "Shared schema v1" begin
    @test SCHEMA_VERSION == "1.0.0"
    @test DNA_POSITIONS == 25:36
    @test DNA_BASE_ORDER == ('A', 'C', 'G', 'T')
    transactions = [[1, 2], [2]]
    labels = Dict(1 => "bread", 2 => "milk")
    prepared = PreparedDataset("groceries", transactions, labels, ["b1", "b2"])
    @test prepared.classes === nothing
    @test prepared.transactions == transactions
    push!(transactions[1], 3)
    @test prepared.transactions[1] == [1, 2]
    dna = PreparedDataset("splice", [[1], [2]], labels, ["splice:1", "splice:2"]; classes=["EI", "N"])
    @test dna.classes == ["EI", "N"]
    @test_throws ArgumentError PreparedDataset("", [[1]], labels, ["b1"])
    @test_throws ArgumentError PreparedDataset("x", [[1]], labels, String[])
    @test_throws ArgumentError PreparedDataset("x", [[1], [1]], labels, ["same", "same"])
    @test_throws ArgumentError PreparedDataset("x", [[1]], Dict(2 => "milk"), ["b1"])
    @test_throws ArgumentError PreparedDataset("x", [[3]], labels, ["b1"])
    @test_throws ArgumentError PreparedDataset("x", [[2, 1]], labels, ["b1"])
    @test_throws ArgumentError PreparedDataset("x", [Int[]], labels, ["b1"])
    @test_throws ArgumentError PreparedDataset("x", [[1]], labels, ["b1"]; classes=["invalid"])
    @test_throws ArgumentError PreparedDataset("x", [[1]], labels, ["b1"]; classes=String[])

    rule = AssociationRule([1], [2], 2, 3, 4, 5)
    @test rule.support == 0.4
    @test rule.confidence ≈ 2/3
    @test rule.lift ≈ 5/6
    @test rule.antecedent == (1,)
    @test_throws ArgumentError AssociationRule([1], [1], 2, 3, 4, 5)
    @test_throws ArgumentError AssociationRule([1], [2], 4, 3, 4, 5)
    @test_throws ArgumentError AssociationRule([1], [2], 1, 4, 4, 5)
    comparison = DNAPatternComparison([1, 6], 2, 0, 1, 4, 5, 10)
    @test comparison.support_EI == 0.5
    @test comparison.support_IE == 0.0
    @test comparison.support_N == 0.1
    @test comparison.support_span == 0.5
    @test_throws ArgumentError DNAPatternComparison([1], 1, 0, 0, 2, 2, 2)
    @test_throws ArgumentError DNAPatternComparison([1, 6], 1, 0, 0, 0, 2, 2)
    @test_throws ArgumentError DNAPatternComparison([1, 6], 3, 0, 0, 2, 2, 2)
    @test_throws ArgumentError splice_transactions("unused"; positions=1:12)
    @test_throws ArgumentError compare_dna_patterns(prepared, Dict{String,Vector{Pattern}}())
    @test_throws ArgumentError compare_dna_patterns(dna, Dict("EI" => Pattern[]))
end

@testset "Association rules and PreparedDataset integration" begin
    data = PreparedDataset("groceries", [[1, 2], [1, 2], [1, 3], [2, 3], [1, 2, 3]],
                           Dict(1 => "bread", 2 => "milk", 3 => "eggs"), string.(1:5))
    for backend in TEST_BACKENDS
        patterns = mine(data.transactions, 1; backend=backend)
        rules = association_rules(patterns, 5; minconf=1//4)
        actual = Dict((r.antecedent, r.consequent) => r for r in rules)
        expected = Dict()
        oracle = brute_force(data.transactions, 1)
        for (a, na) in oracle, (b, nb) in oracle
            isempty(intersect(a, b)) || continue
            key = Tuple(sort!(collect(union(a, b))))
            joint = get(oracle, key, 0)
            joint > 0 && joint//na >= 1//4 || continue
            expected[(a, b)] = (joint, na, nb)
        end
        @test Set(keys(actual)) == Set(keys(expected))
        @test length(rules) == length(expected)
        for (key, (joint, na, nb)) in expected
            r = actual[key]
            @test (r.support_count, r.antecedent_count, r.consequent_count) == (joint, na, nb)
            @test r.confidence == joint/na
            @test r.lift ≈ (joint/na)/(nb/5)
        end
        @test any(r -> length(r.consequent) == 2, rules)
        @test rules == sort(rules; by=r -> (-r.lift, -r.confidence, -r.support,
                       length(r.antecedent)+length(r.consequent), r.antecedent, r.consequent))
        @test [(r.antecedent,r.consequent) for r in association_rules(patterns,5;minconf=0.6)] ==
              [(r.antecedent,r.consequent) for r in association_rules(patterns,5;minconf=3//5)]
    end
    @test isempty(association_rules(Pattern[], 1))
    pairs = [Pattern([1], 100), Pattern([2], 20), Pattern([1, 2], 7)]
    @test length(association_rules(pairs, 200; minconf=1e-6)) == 2
    @test length(association_rules(pairs, 200; minconf=0.07)) == 2
    @test length(association_rules(pairs, 200; minconf=nextfloat(0.07))) == 1
    for invalid in [NaN, Inf, -Inf]
        @test_throws ArgumentError association_rules(pairs, 200; minconf=invalid)
    end
    @test_throws ArgumentError association_rules([Pattern([1, 2], 1)], 1)
    @test_throws ArgumentError association_rules([Pattern([1], 1), Pattern([1], 1)], 1)
    @test_throws ArgumentError association_rules([Pattern([1], 2)], 1)
    @test_throws ArgumentError association_rules(Pattern[], 0)
    @test_throws ArgumentError association_rules(Pattern[], 1; minconf=0)
end
