/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0f172a', // Основной фон (Slate 900)
          800: '#1e293b', // Фон карточек
          700: '#334155',
        },
        primary: {
          400: '#c084fc', // Фиолетовый неон
          500: '#a855f7',
          600: '#9333ea',
        },
        secondary: {
          400: '#22d3ee', // Голубой циан
          500: '#06b6d4',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}