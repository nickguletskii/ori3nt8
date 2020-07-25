import React from "react";
import Layout from "../components/layout";

const NotFoundPage = () => (
  <Layout>
    <section className="section">
      <div className="container">
        <h1 className="title">404: Page not found</h1>
        <p>The requested page does not exist.</p>
      </div>
    </section>
  </Layout>
);

export default NotFoundPage;
