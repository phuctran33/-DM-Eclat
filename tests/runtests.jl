using Test
using Random
using EclatProject

const TEST_BACKENDS = (:list, :bitset)

include("test_io_cli.jl")
# The rule tests reuse the exhaustive oracle defined by the miner tests.
include("test_miner.jl")
include("test_types_rules.jl")
include("test_applications.jl")
