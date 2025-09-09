/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./anomidate_web/templates/**/*.html",
    "./anomidate_web/static/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        'primary': '#ec4899',
        'secondary': '#5865F2',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
