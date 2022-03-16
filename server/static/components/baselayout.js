var BaseLayout = {
    name: 'BaseLayout',
    template: `
    <div class="row">
        <div class="col-4">
            <div class="card">
                <div class="card-body">
                    <ul class="list-group">
                        <router-link v-for="(link, i) in links" :key="i" :to="{ name: link.name }" class="list-group-item">
                            {{ link.text }}
                        </router-link>
                    </ul>
                </div>
            </div>

            <div class="card my-2">
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <a href="https://github.com/Zadigo/zineb" target="_blank" class="btn btn-light btn-block">
                            <i class="fa-brands fa-github me-2"></i>
                            Zineb on Github
                        </a>

                        <a href="https://pypi.org/project/zineb-scrapper/" target="_blank" class="btn btn-light btn-block">
                            <i class="fa-brands fa-python me-2"></i>
                            Zineb on PyPi
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-8">
            <div class="row">
                <div class="col-12">
                    <transition name="general-transition">
                        <router-view></router-view>
                    </transition>
                </div>
            </div>
        </div>
    </div>  
    `,

    data: () => ({
        links: [
            { name: 'home', text: 'Home'},
            { name: 'settings', text: 'Settings'}
        ]
    })
} 
