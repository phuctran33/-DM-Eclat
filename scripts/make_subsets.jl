using Random
using EclatProject

function main(args)
    length(args) in (2, 3) || error("Usage: make_subsets.jl INPUT OUTPUT_DIR [SEED]")
    input, output_dir = args[1:2]
    seed = length(args) == 3 ? parse(Int, args[3]) : 42
    transactions = read_transactions(input)
    isempty(transactions) && error("Input must not be empty")
    order = randperm(MersenneTwister(seed), length(transactions))
    mkpath(output_dir)
    # Nested seeded samples: prevents comparing unrelated random subsets.
    for percent in [10, 25, 50, 75, 100]
        n = max(1, fld(percent * length(transactions), 100))
        open(joinpath(output_dir, "subset_$percent.txt"), "w") do io
            for index in order[1:n]
                println(io, join(transactions[index], ' '))
            end
        end
    end
end

main(ARGS)
