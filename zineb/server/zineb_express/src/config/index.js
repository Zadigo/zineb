module.exports = {
  port: 8081,
  db: {
    database: 'vue_full_stack',
    user: 'test_user',
    password: 'touparet',
    options: {
      host: 'localhost',
      dialect: 'postgres',
      pool: {
        max: 5,
        min: 0,
        acquire: 30000,
        idle: 10000
      }
    }
  }
}
