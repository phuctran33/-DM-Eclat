# The rubric's test entry point delegates to the single shared test suite.
include(joinpath(@__DIR__, "..", "tests", "runtests.jl"))
