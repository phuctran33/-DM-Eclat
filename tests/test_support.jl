@testset "Threshold boundaries and API validation" begin
    @test parse_minsup("0.4") == parse_minsup("40%") == 2 // 5
    @test minimum_count(parse_minsup("0.07"), 100) == 7
    @test minimum_count(parse_minsup("33.3%"), 3) == 1
    @test minimum_count(parse_minsup("0.4"), 6) == 3
    @test minimum_count(parse_minsup("1"), 5) == 5
    @test minimum_count(parse_minsup("0.5"), 0) == 1
    for invalid in ["0", "-1", "1.1", "101%", "NaN", "1e-2", ""]
        @test_throws ArgumentError parse_minsup(invalid)
    end
    @test_throws ArgumentError minimum_count(1 // 2, -1)
    @test_throws ArgumentError mine([[1]], 0)
    @test_throws ArgumentError mine([[2, 1]], 1)
    @test_throws ArgumentError mine([[1]], 1; backend=:invalid)
    @test isempty(mine(Vector{Int}[], 1))
    @test isempty(mine([[1]], 2))
end
