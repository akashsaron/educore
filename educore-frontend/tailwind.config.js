/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary:  { DEFAULT: '#1a2744', light: '#253461' },
        accent:   { DEFAULT: '#4f8ef7', dark: '#3a7de6' },
        success:  '#22c55e',
        warning:  '#f59e0b',
        danger:   '#ef4444',
        muted:    '#6b7a99',
        surface:  '#f4f6fb',
      },
      fontFamily: {
        sans:    ['DM Sans', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      borderRadius: { card: '14px', btn: '8px' },
      boxShadow: {
        card:  '0 1px 3px 0 rgba(0,0,0,0.04), 0 1px 2px 0 rgba(0,0,0,0.03)',
        modal: '0 20px 60px -10px rgba(0,0,0,0.15)',
      },
    },
  },
  plugins: [],
}
