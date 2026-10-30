using Test
using Random
using EclatProject

const TEST_BACKENDS = Symbol.(split(get(ENV, "ECLAT_TEST_BACKENDS", "list"), ','))
all(backend -> backend in [:list, :bitset], TEST_BACKENDS) ||
    error("ECLAT_TEST_BACKENDS must be list, bitset, or list,bitset")

include("test_io.jl")
include("test_support.jl")

if get(ENV, "ECLAT_TEST_MINER", "0") == "1"
    include("test_correctness.jl")
else
    @testset "Eclat correctness: pending implementation" begin
        @test_skip false
    end
    @info "Core is a TODO. M1: ECLAT_TEST_MINER=1 (list). M2/full: also ECLAT_TEST_BACKENDS=list,bitset. Scaffold tests do not establish Eclat correctness."
end

if get(ENV, "ECLAT_TEST_SPMF", "0") == "1"
    include("test_spmf.jl")
else
    @testset "SPMF comparison: pending reference runs" begin
        @test_skip false
    end
end
