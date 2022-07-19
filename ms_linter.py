import pylint.lint
import utility_scripts.zenscraper_0_4 as zs
disable_opts = [
    '--disable=import-error',
    '--disable=wrong-import-position',
    '--disable=attribute-defined-outside-init',
    '--disable=c-extension-no-member',
    '--disable=no-member',
    '--disable=unused-argument'
]
# python_file = 'global_applestore/applestore.py'
python_dir = 'utility_scripts/zenscraper_0_4/utils'

python_files = zs.utils.files.get_file_list(file_dir=python_dir, file_extension='py')

for python_file in python_files:
    pylint_opts = [*disable_opts, python_file]
    pylint.lint.Run(pylint_opts)