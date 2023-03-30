module.exports = (sequelize, dataTypes) => {
  const Spiders = sequelize.define('spiders', {
    name: {
      type: dataTypes.STRING
    },
    description: {
      type: dataTypes.STRING
    },
    created: {
      type: dataTypes.BOOLEAN
    }
  })
  return Spiders
}
