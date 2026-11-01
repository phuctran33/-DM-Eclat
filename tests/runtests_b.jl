# B-only suite: no miner or SPMF implementation is required.
using Test
using Random
using EclatProject
include("test_io.jl")
include("test_support.jl")
include("test_schema.jl")
include("test_applications.jl")
include("test_application_export.jl")
include("test_preparation_cli.jl")
include("test_spmf_references_b.jl")
