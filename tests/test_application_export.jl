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
