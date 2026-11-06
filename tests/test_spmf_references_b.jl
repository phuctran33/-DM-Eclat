using SHA
@testset "B: independently generated SPMF references and provenance" begin
    root=dirname(@__DIR__)
    records=EclatProject.csv_records(joinpath(root,"tests/reference/spmf/manifest.csv"))
    expected_header=["schema_version","dataset","input_path","input_sha256","minsup","min_count","n_transactions","output_path","output_sha256","spmf_version","spmf_jar_sha256","java_version","command","status"]
    @test records[1][2]==expected_header
    @test length(records)==6
    fields=Dict(key=>i for (i,key) in enumerate(records[1][2]))
    @test Set(row[2][fields["dataset"]] for row in records[2:end])==Set(["basic","dense","sparse","duplicates","boundary"])
    for (_,row) in records[2:end]
        name=row[fields["dataset"]]
        input=joinpath(root,"data/toy/$name.txt")
        output=joinpath(root,"tests/reference/spmf/$name.txt")
        transactions=read_transactions(input)
        @test row[fields["schema_version"]]=="1.0.0"
        @test row[fields["status"]]=="ok"
        @test row[fields["minsup"]]=="0.4"
        @test parse(Int,row[fields["min_count"]])==minimum_count(parse_minsup("40%"),length(transactions))
        @test parse(Int,row[fields["n_transactions"]])==length(transactions)
        @test row[fields["input_sha256"]]==bytes2hex(open(sha256,input))
        @test row[fields["output_sha256"]]==bytes2hex(open(sha256,output))
        @test row[fields["spmf_jar_sha256"]]=="c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"
        @test row[fields["spmf_version"]]=="2.64b"
        @test !occursin('\r',read(output,String)) # Git checkout must preserve the declared output hash
        @test read_patterns(output)==read_patterns(joinpath(root,"data/toy/$name.expected.txt"))
        @test occursin("run Eclat",row[fields["command"]])
        @test endswith(row[fields["command"]],"40%")
    end
end
