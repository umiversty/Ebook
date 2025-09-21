import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    svelte({
      compilerOptions: {
        dev: true,
        css: 'injected'
      }
    })
  ],
  test: {
    environment: 'jsdom',
    setupFiles: ['src/setupTests.ts'],
    include: ['**/*.{test,spec}.{js,ts}'],
    globals: true
  }
});
