const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
const config = require('./config')
const { connection } = require('./models')
const morgan = require('morgan')
// const path = require('path')

// const path = __dirname + '/app/views/'
// const vue_app = path.join(__dirname, '/app/views')

const app = express()
// API endpoints
require('./routes')(app)

app.use(morgan('combined'))
app.use(bodyParser.json())
app.use(cors({ origin: 'http://localhost:8080' }))
app.use(bodyParser.urlencoded({ extended: true }))
// app.use(express.static(path))

// Creates and syncs the database and
// then runs the application
connection.sync().then(() => {
  app.listen(process.env.PORT || config.port, () => {
    console.log(`Express server is running on port ${config.port}.`)
  })
})
