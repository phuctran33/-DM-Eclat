using EclatProject
function main(args)
    length(args)==5 || error("Usage: compare_dna.jl RAW EI_PATTERNS IE_PATTERNS N_PATTERNS OUTPUT.csv")
    dataset=splice_transactions(args[1])
    patterns=Dict(label=>Pattern[Pattern(key,count) for (key,count) in read_patterns(path)] for (label,path) in zip(DNA_CLASSES,args[2:4]))
    compared=compare_dna_patterns(dataset,patterns)
    write_dna_comparisons(args[5],dataset,compared)
    println("Compared $(length(compared)) caller-supplied candidates against every class")
end
try
    main(ARGS)
catch err
    showerror(stderr,err); println(stderr); exit(1)
end
