import { defineConfig } from 'vitest/config';

export default defineConfig(async () => {
  const { svelte, vitePreprocess } = await import('@sveltejs/vite-plugin-svelte');
  return {
    plugins: [
      svelte({
        configFile: false,
        preprocess: vitePreprocess()
      })
    ],
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/setupTests.ts'],
      deps: {
        inline: ['@testing-library/jest-dom']
      }
    }
  };
});
