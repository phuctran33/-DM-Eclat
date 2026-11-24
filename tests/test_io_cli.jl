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

@testset "CLI round trip and failure paths" begin
    root = dirname(@__DIR__)
    script = joinpath(root, "scripts", "mine.jl")
    input = joinpath(root, "data", "toy", "basic.txt")
    julia = Base.julia_cmd()
    mktempdir() do directory
        outputs = [joinpath(directory, "$i.txt") for i in 1:3]
        for (i, (flag, value, backend)) in enumerate([
                ("--minsup", "40%", "list"), ("--min-count", "2", "list"),
                ("--minsup", "0.4", "bitset")])
            cmd = `$julia --startup-file=no --project=$root $script --input $input --output $(outputs[i]) $flag $value --backend $backend`
            @test success(pipeline(cmd; stdout=devnull, stderr=devnull))
            @test read_patterns(outputs[i]) == read_patterns(joinpath(root,"tests","reference","spmf","basic.txt"))
        end
        @test read(outputs[1]) == read(outputs[2]) == read(outputs[3])
        before = read(input)
        @test !success(pipeline(`$julia --startup-file=no --project=$root $script --input $input --output $input --min-count 1`;
                              stdout=devnull, stderr=devnull))
        @test read(input) == before
        copy_path = joinpath(directory, "preserve-input.txt")
        alias_path = joinpath(directory, "alias.txt")
        cp(input, copy_path)
        hardlink(copy_path, alias_path)
        @test !success(pipeline(`$julia --startup-file=no --project=$root $script --input $copy_path --output $alias_path --min-count 1`;
                              stdout=devnull, stderr=devnull))
        @test read(copy_path) == before
        @test !success(pipeline(`$julia --startup-file=no --project=$root $script --input $input --output $(outputs[1]) --min-count 1 --minsup 0.4`;
                              stdout=devnull, stderr=devnull))
    end
end
