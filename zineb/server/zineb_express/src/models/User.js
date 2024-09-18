const bcrypt = require('bcrypt')

function hashPassword (user, options) {
  // Function to hash the user's password
  const SALT_FACTOR = 8

  if (!user.changed('password')) {
    return false
  } else {
    return bcrypt.genSaltSync(SALT_FACTOR).then((salt) => {
      bcrypt.hashSync(user.password, salt, null)
    }).then((hash) => {
      return user.setDataValue('password', hash)
    })
  }
}

module.exports = (sequelize, dataTypes) => {
  const User = sequelize.define('users', {
    email: {
      type: dataTypes.STRING,
      unique: true
    },
    password: {
      type: dataTypes.STRING
    }
  }, {
    // Signals that hashes the user's password
    // before create and save, and, on update
    hooks: {
      beforeCreate: hashPassword,
      beforeUpdate: hashPassword,
      beforeSave: hashPassword
    }
  })

  User.prototype.comparePassword = function (password) {
    return bcrypt.compare(password, this.password)
  }

  return User
}
