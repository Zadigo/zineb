<template>
  <div class="container my-5">
    <div class="row">
      <div class="col-5 offset-md-3">
        <div class="card">
          <div class="card-body">
            <input v-model="options.title" type="text" class="form-control mb-2">
            <button type="button" class="btn btn-primary" @click="create">Create</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndexView',
  data () {
    return {
      options: {
        title: null
      }
    }
  },
  methods: {
    async create () {
      try {
        const response = await this.$http.post('/new', this.options)
        console.log(response)
      } catch (e) {
        console.log(e)
      }
    }
  }
}
</script>
