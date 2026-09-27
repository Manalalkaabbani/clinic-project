/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F5F2EA",
        ivory: "#FCFBF7",
        brand: {
          50: "#F1F3F9",
          100: "#E1E7F4",
          500: "#315FC8",
          600: "#244FC0",
          700: "#1B3F9A",
          900: "#172554",
        },
      },
    },
  },
  plugins: [],
}
