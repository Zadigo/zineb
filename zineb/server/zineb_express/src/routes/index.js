const SpidersController = require('../controllers/SpidersController')
const SpidersControllerPolicy = require('../policies/SpidersControllerPolicy')

// List all endpoints that point
// to controllers
module.exports = (app) => {
  app.get(
    '/ping',
    SpidersController.all
  )
  app.post(
    '/new',
    SpidersControllerPolicy.create,
    SpidersController.create
  )
}
