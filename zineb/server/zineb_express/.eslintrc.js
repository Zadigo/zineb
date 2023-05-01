module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: 'standard',
  overrides: [
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'brace-style': 'error',
    'block-scoped-var': 'error',
    'consistent-return': 'warn',
    curly: 'error',
    eqeqeq: 'error',
    'arrow-spacing': [
      'error',
      {
        before: true,
        after: true
      }
    ],
    'default-case': 'error',
    'default-case-last': 'warn',
    'dot-notation': 'error',
    'func-style': [
      'warn',
      'declaration'
    ],
    'no-array-constructor': 'error',
    'no-use-before-define': 'error',
    'no-undef-init': 'error',
    'no-undefined': 'warn',
    'no-bitwise': 'error',
    'no-eq-null': 'error',
    'no-fallthrough': 'error',
    'no-floating-decimal': 'error',
    'no-loop-func': 'error',
    'no-param-reassign': 'error',
    'no-redeclare': 'error',
    'no-return-assign': 'error',
    'no-self-compare': 'warn',
    'no-throw-literal': 'error',
    'no-unneeded-ternary': 'error',
    'prefer-const': 'error',
    radix: 'warn',
    'vars-on-top': 'warn',
    yoda: 'warn'
  }
}
