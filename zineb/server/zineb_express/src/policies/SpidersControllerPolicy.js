const joi = require('joi')

module.exports = {
  create (request, response, next) {
    const schema = {
      name: joi.string().length(50)
    }

    const { error } = joi.validate(request.body, schema)

    if (error) {
      switch (error.details[0].context.key) {
        case 'name':
          response.status(400).send({ name: 'An error for this field' })
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
