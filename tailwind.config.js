/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./dist/**/*.{html,js}'],
  theme: {
    screens:{
      sm: '480px',
      md: '768px',
      lg: '976px',
      xl: '1440px'
    },
    extend: {
      colors: {
        BGColor: '#191A1C',
        BGColorLight: 'hsl(0, 0%, 17%)',
        BGColorDarkLight: '#3d3d3d',
        themeDark: '#48466D',
        themeDarkLight: '#3D84A8',
        themeMain: '#46CDCF',
        themeLight: '#ABEDD8',
      }
    },
  },
  plugins: [],
}
