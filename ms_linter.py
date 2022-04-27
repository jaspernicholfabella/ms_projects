import pylint.lint
disable_opts = [
    '--disable=import-error',
    '--disable=wrong-import-position',
    '--disable=attribute-defined-outside-init',
    '--disable=c-extension-no-member',
    '--disable=unused-argument',
    '--disable=invalid-name',
    '--disable=no-member'
]
pylint_opts = [*disable_opts, 'us_ferc/ferc2.py']
pylint.lint.Run(pylint_opts)