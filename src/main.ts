import './app.css'       // optional, if you already have global styles
import App from './App.svelte'

const app = new App({
  target: document.getElementById('app') as HTMLElement,
})

export default app
