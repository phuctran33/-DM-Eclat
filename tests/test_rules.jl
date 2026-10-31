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
    @test_throws ArgumentError association_rules([Pattern([1, 2], 1)], 1)
    @test_throws ArgumentError association_rules([Pattern([1], 1), Pattern([1], 1)], 1)
    @test_throws ArgumentError association_rules([Pattern([1], 2)], 1)
    @test_throws ArgumentError association_rules(Pattern[], 0)
    @test_throws ArgumentError association_rules(Pattern[], 1; minconf=0)
end
