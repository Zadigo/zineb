const Sequelize = require('sequelize')
const config = require('../config')
// const fs = require('fs')
// const path = require('path')

// TODO: Autoimport all Models
const Spider = require('./Spider')
const User = require('./User')

const connection = new Sequelize(
  config.db.database,
  config.db.user,
  config.db.password,
  config.db.options
)

const database = {
  Sequelize,
  connection,
  Spider: Spider(connection, Sequelize),
  User: User(connection, Sequelize)
}

// TODO: Gets all the models present in the
// the models folder
// fs.readdirSync(__dirname)
//   .filter((file) => {
//     return file !== 'index.js'
//   })
//   .forEach((file) => {
//     const model = connection.import(path.join(__dirname, file))
//     database[model.name] = model
//   })

module.exports = database
