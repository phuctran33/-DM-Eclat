module EclatProject

include("structures.jl")
include("schemas.jl")
include("utils.jl")
include("algorithm/baseline.jl")
include("algorithm/bitset.jl")
include("applications/rules.jl")
include("applications/groceries.jl")
include("applications/dna.jl")

export Itemset, Pattern, PreparedDataset, AssociationRule, DNAPatternComparison,
       SCHEMA_VERSION, DNA_CLASSES, DNA_POSITIONS, DNA_BASE_ORDER,
       read_transactions, write_patterns, read_patterns,
       parse_minsup, minimum_count, mine, association_rules,
       groceries_transactions, splice_transactions, compare_dna_patterns

end
