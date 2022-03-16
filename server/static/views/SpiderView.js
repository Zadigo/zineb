var SpiderView = {
    name: 'SpiderView', 
    template: `
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Spider name</h5>
            
            <hr>

            <h5 class="mb-3">Urls</h5>
            
            <ul class="list-group">
                <a href="http://example.com" class="list-group-item d-flex justify-content-between">
                    <span>http://example.com</span>
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </ul>
        </div>

        <div class="card-footer text-right">
            <button class="btn btn-primary">
                <div v-if="running" class="spinner-grow spinner-grow-sm text-light  me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>

                <i v-else class="fa-solid fa-arrow-right me-2"></i>
                Run spider
            </button>
        </div>
    </div>
    `,
    data: () => ({
        running: true
    }),
    beforeMount () {
        this.setTitle('Spider')
    }
}
