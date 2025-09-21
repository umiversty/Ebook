import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [svelte()],
  resolve: {
    conditions: ['browser', 'module', 'import', 'default']
  },
  test: {
    environment: 'jsdom'
  }
});
