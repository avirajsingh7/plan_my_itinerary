/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      animation: {
        "spin-slow": "spin 2.5s linear infinite",
        "earth-spin": "earthAnim 12s linear infinite",
      },
      keyframes: {
        earthAnim: {
          "0%": { backgroundPositionX: "0" },
          "100%": { backgroundPositionX: "-340px" },
        },
      },
    },
  },
  plugins: [],
};
