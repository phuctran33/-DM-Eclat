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
