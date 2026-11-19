/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: '#070b14',
          card: '#0d1322',
          border: '#1a233a',
          cyan: '#06b6d4',
          cyanGlow: '#22d3ee',
          violet: '#8b5cf6',
          muted: '#64748b',
          crimson: '#ef4444',
          amber: '#f59e0b',
          emerald: '#10b981'
        }
      }
    },
  },
  plugins: [],
}
