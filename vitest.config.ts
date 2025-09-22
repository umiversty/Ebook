import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/setupTests.ts'],
    include: [
      'splitLayout.test.ts',
      'src/**/*.test.ts',
      'src/**/*.spec.ts',
      'src/**/__tests__/**/*.ts'
    ]
  }
});
