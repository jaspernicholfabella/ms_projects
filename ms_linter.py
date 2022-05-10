import pylint.lint
disable_opts = [
    '--disable=import-error',
    '--disable=wrong-import-position',
    '--disable=attribute-defined-outside-init',
    '--disable=c-extension-no-member',
    '--disable=unused-argument',
    '--disable=no-member'
]
# python_file = 'global_manufacturing/h_and_m.py'
python_file = 'utility_scripts/zenscraper.py'
pylint_opts = [*disable_opts, python_file]
pylint.lint.Run(pylint_opts)