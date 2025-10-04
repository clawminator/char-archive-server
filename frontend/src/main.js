import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import './assets/css/root.css'
import store from "./assets/js/store";
import hljsVuePlugin from "@highlightjs/vue-plugin";

const app = createApp(App);
app.use(router).use(store).use(hljsVuePlugin).mount('#app')