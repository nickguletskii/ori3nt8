import React from "react";
import { StaticQuery, graphql } from "gatsby";
import Helmet from "react-helmet";
import ori3nt8Screenshot from "../images/ori3nt8_screenshot.png";

export default () => (
  <StaticQuery
    query={graphql`
      query helmetQuery {
        site {
          siteMetadata {
            title
            author
            description
            keywords
            applicationCategory
            operatingSystems
            downloadURL
          }
        }
      }
    `}
    render={(data) => (
      <Helmet>
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"
        />
        <meta name="description" content={data.site.siteMetadata.description} />
        <meta name="keywords" content={data.site.siteMetadata.keywords} />
        <title>{data.site.siteMetadata.title}</title>
        <html lang="en" />
        <meta itemprop="name" content={data.site.siteMetadata.title} />
        <meta itemprop="author" content={data.site.siteMetadata.author} />
        <meta itemprop="applicationCategory" content={data.site.siteMetadata.applicationCategory} />
        <meta itemprop="operatingSystems" content={data.site.siteMetadata.operatingSystems} />
        <meta itemprop="downloadURL" content={data.site.siteMetadata.downloadURL} />
        <meta
          itemprop="description"
          content={data.site.siteMetadata.description}
        />
        <meta itemprop="image" content={ori3nt8Screenshot} />
      </Helmet>
    )}
  />
);
