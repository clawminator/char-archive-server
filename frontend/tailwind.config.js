/** @type {import('tailwindcss').Config} */
module.exports = {
    // darkMode: false,
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
        "./node_modules/tw-elements/dist/js/**/*.js",
        "./node_modules/flowbite/**/*.js"
    ],
    // corePlugins: {
    //     preflight: false, // we'll manually do the reset ourselves since buttons were being broken
    // },
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/typography'),
        require("tw-elements/dist/plugin.cjs"),
        require('flowbite/plugin')
    ],
}

