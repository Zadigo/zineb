const joi = require('joi')

module.exports = {
  // Used to check that that the data passed
  // to the database respect a set of constraints
  create (request, response, next) {
    const schema = {
      email: joi.string().email(),
      password: joi.string().regex(/[a-zA-Z0-9]/)
    }

    const { error } = joi.validate(request.body, schema)

    if (error) {
      switch (error.details[0].context.key) {
        case 'email':
          response.status(400).send({ email: 'An error for this field' })
          break
        case 'password':
          response.status(400).send({ email: 'An error for this field' })
          break
        default:
          response.status(400).send({ other: 'An error for this field' })
          break
      }
    } else {
      next()
    }
  }
}
