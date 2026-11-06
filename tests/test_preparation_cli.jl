@testset "B: real preprocessing CLI and supplied-pattern CLI" begin
    root=dirname(@__DIR__); julia=Base.julia_cmd()
    prep=joinpath(root,"scripts","prepare_applications.jl")
    compare=joinpath(root,"scripts","compare_dna.jl")
    mktempdir() do dir
        input=joinpath(dir,"groceries.csv");output=joinpath(dir,"grocery-output")
        write(input,"basket_id,item_name\n01,milk\n01,bread\n02,bread\n")
        command=`$julia --startup-file=no --project=$root $prep groceries $input $output`
        @test success(pipeline(command;stdout=devnull,stderr=devnull))
        @test read_transactions(joinpath(output,"transactions.txt"))==[[1,2],[1]]
        before=read(joinpath(output,"transactions.txt"))
        @test !success(pipeline(command;stdout=devnull,stderr=devnull))
        @test read(joinpath(output,"transactions.txt"))==before
        @test !success(pipeline(`$julia --startup-file=no --project=$root $prep unknown $input $output`;stdout=devnull,stderr=devnull))
        raw=joinpath(dir,"splice.data")
        write(raw,"EI,e,$(dna_fixture(repeat("A",12)))\nIE,i,$(dna_fixture(repeat("C",12)))\nN,n,$(dna_fixture(repeat("G",12)))\n")
        dna_output=joinpath(dir,"dna-output")
        @test success(pipeline(`$julia --startup-file=no --project=$root $prep splice $raw $dna_output`;stdout=devnull,stderr=devnull))
        @test length(read_transactions(joinpath(dna_output,"transactions.txt")))==3
        patterns=[joinpath(dir,"$label.txt") for label in DNA_CLASSES]
        for (path,items) in zip(patterns,["1 5","2 6","3 7"])
            write(path,"$items #SUP: 1\n")
        end
        result=joinpath(dir,"patterns.csv")
        cmd=`$julia --startup-file=no --project=$root $compare $raw $(patterns[1]) $(patterns[2]) $(patterns[3]) $result`
        @test success(pipeline(cmd;stdout=devnull,stderr=devnull))
        @test length(EclatProject.csv_records(result))==4
        before=read(result);write(patterns[1],"1 5 #SUP: 99\n")
        @test !success(pipeline(cmd;stdout=devnull,stderr=devnull))
        @test read(result)==before
    end
end
