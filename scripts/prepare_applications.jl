using EclatProject
function main(args)
    length(args)==3 || error("Usage: prepare_applications.jl groceries|splice INPUT OUTPUT_DIRECTORY")
    name,input,output=args
    prepared=name=="groceries" ? prepare_groceries(input) : name=="splice" ? prepare_splice(input) : error("Unknown dataset")
    write_prepared_dataset(prepared.dataset,output; source_ids=prepared.source_ids,audit=prepared.audit)
    println("dataset=$name, observations=$(length(prepared.dataset.transactions)), mapped_items=$(length(prepared.dataset.item_labels))")
    for row in prepared.audit
        println("class=$(row[3]), reason=$(row[4]), count=$(row[5])")
    end
end
try
    main(ARGS)
catch err
    showerror(stderr,err); println(stderr); exit(1)
end
