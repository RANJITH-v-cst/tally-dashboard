/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#0b1020',
          card: '#121a33',
          soft: '#1a2447',
        },
        brand: {
          DEFAULT: '#5b8cff',
          400: '#7aa0ff',
          600: '#4171e8',
        },
        accent: {
          mint: '#3ed6a8',
          gold: '#f4c95d',
          rose: '#ff7d7d',
          violet: '#b794f4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,.2), 0 8px 24px rgba(15,23,42,.35)',
      },
    },
  },
  plugins: [],
};
