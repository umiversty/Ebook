/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
  globals: true,
  environment: 'happy-dom', // or 'jsdom'
  setupFiles: ['./src/tests/setup.ts'],
}
});
