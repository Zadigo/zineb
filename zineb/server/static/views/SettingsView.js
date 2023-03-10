var SettingsView = {
    name: 'SettingsView', 
    template: `
    <div class="card">
        <div class="card-body">
            Settings
        </div>
    </div>
    `,
    beforeMount() {
        this.setTitle('Settings')
    }
}
