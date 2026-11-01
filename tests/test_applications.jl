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
