/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        fond: '#F4F5FB',
        surface: '#FFFFFF',
        barre: '#F8F9FC',
        encre: '#1E293B',
        muet: '#64748B',
        trait: '#E8EAF2',
        indigo: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
        },
      },
      boxShadow: {
        carte: '0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06)',
        douce: '0 1px 3px rgba(15, 23, 42, 0.06)',
      },
      borderRadius: {
        carte: '1rem',
        bouton: '0.75rem',
      },
    },
  },
  plugins: [],
}
