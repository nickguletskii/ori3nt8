import "./style.scss";
import React from "react";
import Helmet from "./helmet";
import Footer from "./footer";
import Navbar from "./navbar";

const Layout = ({ children, includeNavbar = true }) => (
  <div>
    <Helmet />
    {includeNavbar ? <Navbar /> : null}
    {children}
    <Footer />
  </div>
);

export default Layout;
