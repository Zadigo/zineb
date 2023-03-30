const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes: [
        {
            path: '/',
            component: BaseLayout,
            children: [
                {
                    path: '',
                    name: 'home_view',
                    component: SpidersView
                },
                {
                    path: 'spider/:id(\d+)',
                    name: 'spider_view',
                    component: SpiderView
                },
                {
                    path: 'settings',
                    name: 'settings_view',
                    component: SettingsView
                }
            ]

        }
    ]
})
