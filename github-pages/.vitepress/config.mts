import { defineConfig } from 'vitepress'

const repo = 'https://github.com/aidevme/copilot-studio-custom-mcp-samples'

// GitHub Pages serves the site as a project site under /<repository>/.
export default defineConfig({
  title: 'Custom MCP servers for Copilot Studio',
  description: 'Samples for the aidevme.com series: one demo agent, built with Logic Apps, API Management and C#.',
  lang: 'en-US',
  base: '/copilot-studio-custom-mcp-samples/',
  cleanUrls: true,

  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/' },
      { text: 'Series', link: '/guide/series' },
      { text: 'Blog', link: 'https://aidevme.com/copilot-studio-custom-mcp-servers-when-you-need-one/' }
    ],

    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Overview', link: '/guide/' },
          { text: 'The series', link: '/guide/series' },
          { text: 'The tool contract', link: '/guide/tool-contract' },
          { text: 'Build paths', link: '/guide/build-paths' }
        ]
      },
      {
        text: 'Run it',
        items: [
          { text: 'Run locally', link: '/guide/run-locally' },
          { text: 'Provision Azure', link: '/guide/provisioning' }
        ]
      }
    ],

    socialLinks: [{ icon: 'github', link: repo }],

    search: { provider: 'local' },

    footer: {
      message: 'Demo data only. Released under the MIT License.',
      copyright: '© 2026 Zsolt Zombik'
    }
  }
})
