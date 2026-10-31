using Test
using Random
using EclatProject

const TEST_BACKENDS = Symbol.(split(get(ENV, "ECLAT_TEST_BACKENDS", "list,bitset"), ','))
all(backend -> backend in [:list, :bitset], TEST_BACKENDS) ||
    error("ECLAT_TEST_BACKENDS must be list, bitset, or list,bitset")

include("test_io.jl")
include("test_support.jl")
include("test_schema.jl")

if get(ENV, "ECLAT_TEST_MINER", "1") == "1"
    include("test_correctness.jl")
    include("test_rules.jl")
    include("test_cli.jl")
else
    @testset "Eclat correctness: pending implementation" begin
        @test_skip false
    end
    @info "Miner tests explicitly disabled by ECLAT_TEST_MINER=0."
end

if get(ENV, "ECLAT_TEST_SPMF", "1") == "1"
    include("test_spmf.jl")
else
    @testset "SPMF comparison: pending reference runs" begin
        @test_skip false
    end
end
