import pylint.lint
disable_opts = [
    '--disable=import-error',
    '--disable=wrong-import-position',
    '--disable=attribute-defined-outside-init',
    '--disable=c-extension-no-member',
    '--disable=no-member',
    '--disable=unused-argument'
]
# python_file = 'global_applestore/applestore.py'
python_file = 'utility_scripts/zenscraper_0_3.py'
pylint_opts = [*disable_opts, python_file]
pylint.lint.Run(pylint_opts)