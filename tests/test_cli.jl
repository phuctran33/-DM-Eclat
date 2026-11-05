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
        @test !success(pipeline(`$julia --startup-file=no --project=$root $script --input $input --output $(outputs[1]) --min-count 1 --minsup 0.4`;
                              stdout=devnull, stderr=devnull))
    end
end
