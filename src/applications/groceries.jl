"""TODO (B, M2): canonical CSV basket_id,item_name -> PreparedDataset.

One basket is one transaction; distinct product names -> positive integer IDs.
Normalize names with NFC, lowercase, strip and collapse whitespace. Sort labels
for IDs 1..m and basket IDs lexicographically for row order. Preserve identical
baskets with distinct IDs; reject blank IDs/names. classes=nothing.
Source-specific import belongs in the notebook adapter. See docs/SCHEMA.md.
"""
function groceries_transactions(path::AbstractString)::PreparedDataset
    error("TODO M2 / B: implement Groceries preparation, mapping and statistics")
end
