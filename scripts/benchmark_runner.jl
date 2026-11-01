# Julia entry point; the controller uses Python 3.11+ stdlib for process/CSV/TOML.
python = get(ENV, "PYTHON", "python3")
script = joinpath(@__DIR__, "benchmark_runner.py")
run(`$python $script --julia $(joinpath(Sys.BINDIR, Base.julia_exename())) $ARGS`)
