"""TODO (B, M2): Groceries raw data -> sorted transactions + reversible mapping.

One basket is one transaction; distinct product names -> positive integer IDs.
Fix a sorted vocabulary, save item_id -> product_name, retain duplicate baskets.
Document the actual source schema before parsing: exports may differ.
"""
function groceries_transactions(path::AbstractString)
    error("TODO M2 / B: implement Groceries preparation, mapping and statistics")
end
