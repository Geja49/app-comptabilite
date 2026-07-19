/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        fond: '#F1F4F9',
        surface: '#FFFFFF',
        barre: '#F8FAFC',
        encre: '#0F172A',
        muet: '#64748B',
        trait: '#E2E8F0',
        accent: {
          DEFAULT: '#1D4ED8',
          soft: '#DBEAFE',
          dark: '#1E3A8A',
        },
        indigo: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#3B82F6',
          600: '#1D4ED8',
          700: '#1E40AF',
        },
      },
      boxShadow: {
        carte: '0 1px 2px rgba(15, 23, 42, 0.04), 0 10px 28px rgba(15, 23, 42, 0.05)',
        douce: '0 1px 2px rgba(15, 23, 42, 0.05)',
        focus: '0 0 0 4px rgba(29, 78, 216, 0.15)',
      },
      borderRadius: {
        carte: '1.1rem',
        bouton: '0.8rem',
      },
    },
  },
  plugins: [],
}
