using Test
using Random
using EclatProject

const TEST_BACKENDS = (:list, :bitset)

include("test_io.jl")
include("test_support.jl")
include("test_schema.jl")
include("test_applications.jl")
include("test_application_export.jl")
include("test_preparation_cli.jl")
include("test_spmf_references_b.jl")

include("test_correctness.jl")
include("test_rules.jl")
include("test_cli.jl")
include("test_application_pipeline.jl")
include("test_spmf.jl")
