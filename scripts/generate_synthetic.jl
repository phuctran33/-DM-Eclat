using Random

function main(args)
    length(args) in (4, 5) || error("Usage: generate_synthetic.jl OUTPUT N_ITEMS N_TRANSACTIONS LENGTH [SEED]")
    path = args[1]
    items, rows, width = parse.(Int, args[2:4])
    seed = length(args) == 5 ? parse(Int, args[5]) : 42
    1 <= width <= items || error("Require 1 <= LENGTH <= N_ITEMS")
    rows > 0 || error("N_TRANSACTIONS must be positive")
    rng = MersenneTwister(seed)
    mkpath(dirname(abspath(path)))
    open(path, "w") do io
        for _ in 1:rows
            println(io, join(sort!(randperm(rng, items)[1:width]), ' '))
        end
    end
end

main(ARGS)
