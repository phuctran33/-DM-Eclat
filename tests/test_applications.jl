using TOML

@testset "B: CSV and Groceries normalization" begin
    mktempdir() do dir
        path=joinpath(dir,"input.csv")
        write(path,"basket_id,item_name\n002, Milk \n001,Bread\n001,bread\n003,Caf\u00e9\n004,Cafe\u0301\n005,Milk\n")
        prepared=prepare_groceries(path); data=prepared.dataset
        @test data.row_ids==["001","002","003","004","005"]
        @test data.item_labels==Dict(1=>"bread",2=>"caf\u00e9",3=>"milk")
        @test data.transactions==[[1],[3],[2],[2],[3]]
        @test data.classes===nothing
        @test prepared.audit[2][5]==1
        @test groceries_transactions(path).transactions==data.transactions
        output=joinpath(dir,"processed")
        write_prepared_dataset(data,output; source_ids=prepared.source_ids,audit=prepared.audit)
        @test read_transactions(joinpath(output,"transactions.txt"))==data.transactions
        @test EclatProject.csv_records(joinpath(output,"observations.csv"))[2][2]==["1","001","001",""]
        @test_throws ArgumentError write_prepared_dataset(data,output)
        write(path,"\ufeffbasket_id,item_name\r\n01,\"tomato, canned\"\r\n01,\"special \"\"mix\"\"\"\r\n02,\"line\r\nbreak\"\r\n")
        @test Set(values(groceries_transactions(path).item_labels))==Set(["tomato, canned","special \"mix\"","line break"])
        for bad in ["wrong,header\n","basket_id,item_name\n","basket_id,item_name\n,item\n","basket_id,item_name\n01,  \n","basket_id,item_name\n01,x,y\n","basket_id,item_name\n01,\"open\n","basket_id,item_name\n01,\"x\"junk\n","basket_id,item_name\n01,ba\"d\n"]
            write(path,bad)
            @test_throws ArgumentError groceries_transactions(path)
        end
    end
end
function dna_fixture(window; outside=false)
    sequence=fill('T',60); sequence[25:36]=collect(window)
    outside && (sequence[1]='N')
    return join(sequence)
end
@testset "B: Splice normalization and independent class comparison" begin
    mktempdir() do dir
        path=joinpath(dir,"splice.data")
        a=dna_fixture(repeat("A",12)); c=dna_fixture(repeat("C",12))
        n=dna_fixture("AA"*repeat("G",10)); ambiguous=dna_fixture("N"*repeat("A",11))
        outside=dna_fixture("AA"*repeat("G",10); outside=true)
        write(path,"EI,id1,$a\nIE,id2,$c\nN,id3,$n\nEI,drop,$ambiguous\nN,id4,$outside\nEI,id1,$a\n")
        prepared=prepare_splice(path); data=prepared.dataset
        @test length(data.transactions)==5
        @test data.classes==["EI","IE","N","N","EI"]
        @test data.row_ids==["splice:1","splice:2","splice:3","splice:5","splice:6"]
        @test prepared.source_ids==["id1","id2","id3","id4","id1"]
        @test length(data.item_labels)==48
        @test data.item_labels[1]=="pos=-6;base=A"
        @test data.item_labels[25]=="pos=+1;base=A"
        @test data.item_labels[48]=="pos=+6;base=T"
        @test all(t->length(t)==12 && issorted(t) && allunique(t),data.transactions)
        @test data.transactions[1]==data.transactions[5]
        @test any(row->row[3]=="EI" && row[4]=="ambiguous_window" && row[5]==1,prepared.audit)
        patterns=Dict("EI"=>[Pattern([1,5],2)],"IE"=>[Pattern([2,6],1)],"N"=>Pattern[])
        compared=compare_dna_patterns(data,patterns)
        @test [p.items for p in compared]==[(1,5),(2,6)]
        p=compared[1]
        @test (p.count_EI,p.count_IE,p.count_N)==(2,0,2)
        @test (p.n_EI,p.n_IE,p.n_N)==(2,1,2)
        @test p.support_N==1.0
        write_dna_comparisons(joinpath(dir,"patterns.csv"),data,compared)
        @test length(EclatProject.csv_records(joinpath(dir,"patterns.csv")))==3
        @test_throws ArgumentError prepare_splice(path; positions=1:12)
        @test_throws ArgumentError compare_dna_patterns(data,Dict("EI"=>Pattern[]))
        @test_throws ArgumentError compare_dna_patterns(data,Dict("EI"=>[Pattern([1,2],1)],"IE"=>Pattern[],"N"=>Pattern[]))
        for bad in ["EI,id,ACG\n","XX,id,$a\n","EI,,$a\n","EI,id,$(replace(a,'A'=>'X'))\n","EI,id,$a\n"]
            write(path,bad)
            @test_throws ArgumentError prepare_splice(path)
        end
    end
end

@testset "B: RFC4180 writer, record positions and rule artifacts" begin
    mktempdir() do dir
        path=joinpath(dir,"records.csv")
        EclatProject.write_csv_table(path,("first","second"),[("a,b","quoted \"text\""),("line\nbreak",""),("Ti\u1ebfng Vi\u1ec7t","caf\u00e9")])
        records=EclatProject.csv_records(path)
        @test [record[2] for record in records]==[["first","second"],["a,b","quoted \"text\""],["line\nbreak",""],["Ti\u1ebfng Vi\u1ec7t","caf\u00e9"]]
        write(path,"a,b\r\n\"x\ry\",z\r\nlast,row\r\n")
        @test [record[1] for record in EclatProject.csv_records(path)]==[1,2,4]
        write(path,"a,b\n\n\"\",\n")
        @test [record[2] for record in EclatProject.csv_records(path)]==[["a","b"],["",""]]
        dataset=PreparedDataset("groceries",[[1,2],[1,2],[1]],Dict(1=>"bread",2=>"milk"),["1","2","3"])
        rules=[AssociationRule([1],[2],2,3,2,3),AssociationRule([2],[1],2,2,3,3)]
        write_association_rules(path,dataset,rules)
        records=EclatProject.csv_records(path)
        @test length(records)==3
        @test records[2][2][2:5]==["2","1","milk","bread"]
        @test parse(Float64,records[2][2][12])==1.0
        write_association_rules(path,dataset,rules;top_k=1)
        @test length(EclatProject.csv_records(path))==2
        write_association_rules(path,dataset,AssociationRule[])
        @test length(EclatProject.csv_records(path))==1
        @test_throws ArgumentError write_association_rules(path,dataset,rules;top_k=0)
        @test_throws ArgumentError write_association_rules(path,dataset,[rules[1],rules[1]])
        @test_throws ArgumentError write_association_rules(path,dataset,[AssociationRule([1],[2],1,2,2,4)])
        @test_throws ArgumentError write_association_rules(path,dataset,[AssociationRule([3],[1],1,1,2,3)])
    end
end
@testset "B: reject inconsistent DNA patterns and export ranking" begin
    a=collect(1:4:45); c=collect(2:4:46); n=vcat([1,5],collect(11:4:47))
    mapping=EclatProject.dna_item_labels()
    data=PreparedDataset("splice",[a,a,c,n,n],mapping,string.(1:5);classes=["EI","EI","IE","N","N"])
    patterns=Dict("EI"=>[Pattern([1,5],2)],"IE"=>[Pattern([2,6],1)],"N"=>Pattern[])
    wrong=deepcopy(patterns);wrong["EI"]=[Pattern([1,5],1)]
    @test_throws ArgumentError compare_dna_patterns(data,wrong)
    duplicate=deepcopy(patterns);push!(duplicate["EI"],duplicate["EI"][1])
    @test_throws ArgumentError compare_dna_patterns(data,duplicate)
    wrong=deepcopy(patterns);wrong["EI"]=[Pattern([49,50],1)]
    @test_throws ArgumentError compare_dna_patterns(data,wrong)
    wrongmap=copy(mapping);wrongmap[1]="wrong token"
    invalid=PreparedDataset("splice",data.transactions,wrongmap,data.row_ids;classes=data.classes)
    @test_throws ArgumentError compare_dna_patterns(invalid,patterns)
    invalidrows=deepcopy(data.transactions);invalidrows[1][2]=2
    invalid=PreparedDataset("splice",invalidrows,mapping,data.row_ids;classes=data.classes)
    @test_throws ArgumentError compare_dna_patterns(invalid,patterns)
    mktempdir() do dir
        path=joinpath(dir,"comparison.csv")
        compared=compare_dna_patterns(data,patterns)
        write_dna_comparisons(path,data,reverse(compared))
        rows=EclatProject.csv_records(path)
        @test rows[2][2][2]=="1 5"
        @test rows[3][2][2]=="2 6"
    end
end

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
        # The input root can contain arbitrary data; it is never the code root.
        mkpath(joinpath(dir,"src"))
        write(joinpath(dir,"src","input_only.jl"),"not application source")
        output=joinpath(dir,"result")
        metadata=run_applications(cfg,output;root=dir)
        @test haskey(metadata["source_sha256"],"src/EclatProject.jl")
        @test metadata["source_sha256"]["scripts/run_applications.jl"] == bytes2hex(open(sha256,joinpath(@__DIR__,"..","scripts","run_applications.jl")))
        @test !haskey(metadata["source_sha256"],"src/input_only.jl")
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
