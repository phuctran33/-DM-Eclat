@testset "SPMF I/O and canonical comparison" begin
    mktempdir() do directory
        input = joinpath(directory, "input.txt")
        write(input, "@FILETYPE=example\n# comment\n% comment\n\n1 2 3\n1 2 3\n2 4\n")
        @test read_transactions(input) == [[1, 2, 3], [1, 2, 3], [2, 4]]
        for invalid in ["2 1\n", "1 1\n", "0 1\n", "-1 2\n", "1 x\n"]
            write(input, invalid)
            @test_throws ArgumentError read_transactions(input)
        end
        output = joinpath(directory, "output.txt")
        write_patterns(output, [Pattern([3, 1], 2), Pattern([2], 4)])
        @test read_patterns(output) == Dict((1, 3) => 2, (2,) => 4)
        write(output, "@FILETYPE=patterns\n3 1 #SUP: 2\n2 #SUP: 4\n")
        @test read_patterns(output) == Dict((1, 3) => 2, (2,) => 4)
        write(output, "1 3 #SUP: 2\n3 1 #SUP: 2\n")
        @test_throws ArgumentError read_patterns(output)
        @test_throws ArgumentError write_patterns(output, [Pattern([1], 1), Pattern([1], 2)])
        @test_throws ArgumentError Pattern([1, 1], 1)
        @test_throws ArgumentError Pattern([0], 1)
        @test_throws ArgumentError Pattern(Int[], 1)
        @test_throws ArgumentError Pattern([1], 0)
    end
end
