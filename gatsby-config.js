module.exports = {
  siteMetadata: {
    title: "Ori3nt8",
    author: "Nick Guletskii",
    description:
      "Software for automatically rotating photos/fixing the JPEG orientation using a neural network",
    keywords: "Image, Photo, Rotation, Orientation",
    github: "https://github.com/nickguletskii/ori3nt8",
    siteUrl: "https://ori3nt8.nickguletskii.com",
  },
  plugins: [
    "gatsby-plugin-react-helmet",
    {
      resolve: "gatsby-source-filesystem",
      options: {
        name: "images",
        path: `${__dirname}/src/images`,
      },
    },
    "gatsby-transformer-sharp",
    "gatsby-plugin-sharp",
    "gatsby-plugin-sass",
    {
      resolve: "gatsby-plugin-google-analytics",
      options: {
        trackingId: "UA-XXXXXXXX-X",
        anonymize: true,
      },
    },
    "gatsby-plugin-sitemap",
  ],
};
