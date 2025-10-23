// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      // 1) Your custom text-shadow scales
      textShadow: {
        DEFAULT: '0 1px 2px rgba(0,0,0,0.5)',
        md:      '0 2px 4px rgba(0,0,0,0.6)',
      },
      // 2) Your custom fonts
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        pop:  ['Poppins', 'ui-sans-serif', 'system-ui'],
        robo: ['Roboto', 'ui-sans-serif', 'system-ui'],
      },
    }
  },
  plugins: [
    // 3) The text-shadow utility generator
    function ({ addUtilities, theme }) {
      const shadows = theme('textShadow')
      const utilities = Object.entries(shadows).map(([name, value]) => ({
        [`.text-shadow${name === 'DEFAULT' ? '' : '-' + name}`]: {
          textShadow: value,
        }
      }))
      addUtilities(utilities)
    }
  ]
}
