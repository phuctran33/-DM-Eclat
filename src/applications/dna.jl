"""TODO (B, M2): UCI Splice -> position/base transactions and EI/IE/N labels.

Frozen v1: positions 25:36 of each 60-base sequence (Julia 1-based), relative
-6..-1,+1..+6. Map item_id=4*(slot-1)+base_index, base order A,C,G,T.
Read UCI's three CSV fields class,source_id,sequence; uppercase class/sequence,
remove sequence whitespace. Reject malformed rows; drop a sample only when its
12-position window contains an IUPAC ambiguity symbol. Keep source row order,
row_ids="splice:<source_line>"; labels are metadata. Return all 48 mapping entries.
"""
function splice_transactions(path::AbstractString; positions=DNA_POSITIONS)::PreparedDataset
    collect(positions) == collect(DNA_POSITIONS) ||
        throw(ArgumentError("Schema v1 fixes the DNA window to positions 25:36"))
    error("TODO M2 / B: implement Splice parser, position/base mapping and class metadata")
end

"""TODO: compare class-specific support for shared 2–4-item patterns.

Mine complete frequent outputs first; filter 2–4-item patterns for presentation.
When a candidate is infrequent/absent in another class, count it directly there;
absence from that class's frequent output does NOT imply zero support.
"""
function compare_dna_patterns(dataset::PreparedDataset,
                             patterns_by_class::AbstractDict{String,Vector{Pattern}})::Vector{DNAPatternComparison}
    dataset.classes !== nothing || throw(ArgumentError("DNA class metadata is required"))
    Set(keys(patterns_by_class)) == Set(DNA_CLASSES) ||
        throw(ArgumentError("patterns_by_class must contain EI, IE and N"))
    error("TODO M2 / B: compare EI, IE, N with class-specific denominators")
end
