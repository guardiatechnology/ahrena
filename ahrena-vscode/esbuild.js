const esbuild = require('esbuild');
const path = require('path');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/** @type {import('esbuild').BuildOptions} */
const baseConfig = {
  bundle: true,
  external: ['vscode'],
  format: 'cjs',
  platform: 'node',
  target: 'node18',
  sourcemap: !production,
  minify: production,
  logLevel: 'info',
};

async function build() {
  // Main extension bundle
  const extensionCtx = await esbuild.context({
    ...baseConfig,
    entryPoints: ['src/extension.ts'],
    outfile: 'dist/extension.js',
  });

  // Test runner bundle
  const testCtx = await esbuild.context({
    ...baseConfig,
    entryPoints: ['test/suite/index.ts'],
    outfile: 'dist/test/suite/index.js',
  });

  if (watch) {
    await Promise.all([extensionCtx.watch(), testCtx.watch()]);
    console.log('Watching for changes...');
  } else {
    await Promise.all([extensionCtx.rebuild(), testCtx.rebuild()]);
    await Promise.all([extensionCtx.dispose(), testCtx.dispose()]);
  }
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
