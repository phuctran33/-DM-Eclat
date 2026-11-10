using TOML
include(joinpath(@__DIR__,"..","scripts","run_applications.jl"))

@testset "M2: complete mining applications and output ownership" begin
    mktempdir() do dir
        groceries=joinpath(dir,"groceries.csv")
        write(groceries,"basket_id,item_name\n1,bread\n1,milk\n1,eggs\n2,bread\n2,milk\n3,bread\n3,eggs\n4,milk\n4,eggs\n5,bread\n5,milk\n5,eggs\n")
        data=groceries_transactions(groceries)
        before=deepcopy(data.transactions)
        result=groceries_application(data;minsup="40%",minconf="0.60",top_k=3)
        @test result.min_count==2
        @test length(result.patterns)==7
        @test length(result.rules)==9
        @test result.top10==result.rules[1:3]
        @test data.transactions==before
        @test isempty(groceries_application(data;minsup="40%",minconf="0.99").rules)
        @test_throws ArgumentError groceries_application(data;top_k=0)
        @test_throws ArgumentError groceries_application(data;minconf="0")
        @test_throws ArgumentError groceries_application(data;minsup="0")
        raw=joinpath(dir,"splice.data")
        bases="ACGT"
        open(raw,"w") do io
            for label in DNA_CLASSES, sample in 1:4
                pair=label=="EI" ? "AA" : label=="IE" ? "CC" : repeat(string(bases[sample]),2)
                window=pair*join(bases[mod1(i+sample,4)] for i in 1:10)
                sequence=repeat("T",24)*window*repeat("T",24)
                println(io,"$label,$label-$sample,$sequence")
            end
        end
        dna=splice_transactions(raw)
        compared=dna_application(dna;minsup="0.75")
        @test compared.min_counts==Dict("EI"=>3,"IE"=>3,"N"=>3)
        @test length(compared.comparisons)==2
        @test isempty(compared.patterns_by_class["N"])
        @test all(p->p.count_N==1 && p.support_N==0.25,compared.comparisons)
        @test_throws ArgumentError dna_application(data)
        @test_throws ArgumentError groceries_application(dna)
        config=TOML.parsefile(joinpath(@__DIR__,"..","configs","applications.toml"))
        config["groceries"]["input"]="groceries.csv"
        config["groceries"]["minsup"]="40%"
        config["groceries"]["top_k"]=3
        config["dna"]["input"]="splice.data"
        config["dna"]["minsup"]="0.75"
        cfg=joinpath(dir,"applications.toml")
        open(io->TOML.print(io,config;sorted=true),cfg,"w")
        output=joinpath(dir,"result")
        metadata=run_applications(cfg,output;root=dir)
        @test metadata["statistics"]["groceries"]["n_rules"]==9
        @test length(EclatProject.csv_records(joinpath(output,"groceries_top10.csv")))==4
        @test length(EclatProject.csv_records(joinpath(output,"dna_patterns.csv")))==3
        @test length(read_patterns(joinpath(output,"patterns","groceries.txt")))==7
        @test metadata["statistics"]["dna"]["classes"]["N"]["n_patterns"]==0
        saved=Dict(replace(relpath(joinpath(folder,f),output),'\\'=>'/')=>read(joinpath(folder,f))
            for (folder,_,files) in walkdir(output) for f in files)
        @test_throws ArgumentError run_applications(cfg,output;root=dir)
        @test all(read(joinpath(output,path))==bytes for (path,bytes) in saved)
        @test all(bytes2hex(sha256(read(joinpath(output,path))))==hash for (path,hash) in metadata["artifact_sha256"])
        config["dna"]["positions_1based"]=collect(1:12)
        open(io->TOML.print(io,config;sorted=true),cfg,"w")
        @test_throws ArgumentError run_applications(cfg,joinpath(dir,"invalid");root=dir)
        @test !ispath(joinpath(dir,"invalid"))
    end
end
