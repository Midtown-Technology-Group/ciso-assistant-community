import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sidebar from './src/generated/sidebar.mjs';

export default defineConfig({
  site: 'https://docs.ciso.midtowntg.com',
  integrations: [
    starlight({
      title: 'CISO Assistant',
      description: 'Static documentation for CISO Assistant and MTG MSP tenancy work.',
      logo: {
        src: './public/.gitbook/assets/gh_banner.png',
        alt: 'CISO Assistant',
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/Midtown-Technology-Group/ciso-assistant-community',
        },
      ],
      sidebar,
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 3,
      },
    }),
  ],
});
