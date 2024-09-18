// const db = require('../models')
// const Tutorial = db.tutorials
// const Op = db.Sequelize.Op

// List actions for endpoints here

const { Spiders } = require('../models')

module.exports = {
  async all (request, response) {
    try {
      const result = await Spiders.findAll()
      console.log(result)
      response.send(result.toJson())
      response.send({ message: 'works' })
    } catch (e) {
      console.error(e)
      response.status(400).send({
        error: `Something went wrong ${e}`
      })
    }
  },

  async create (request, response) {
    try {
      await Spiders.create(request.body)
      console.log(request.body)
      response.send({ a: true })
    } catch (e) {
      response.status(400).send({
        e: 'Something went wrong'
      })
    }
  }
}

// // Create and Save a new Tutorial
// exports.create = (request, response) => {
//   response.send({ message: 'works' })
// }

// // Retrieve all Tutorials from the database.
// exports.findAll = (request, response) => {

// }

// // Find a single Tutorial with an id
// exports.findOne = (request, response) => {

// }

// // Update a Tutorial by the id in the request
// exports.update = (request, response) => {

// }

// // Delete a Tutorial with the specified id in the request
// exports.delete = (request, response) => {

// }

// // Delete all Tutorials from the database.
// exports.deleteAll = (request, response) => {

// }

// // Find all published Tutorials
// exports.findAllPublished = (request, response) => {

// }
