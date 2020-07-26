import "./style.scss";
import React from "react";
import { FaDownload } from "react-icons/fa";

import ori3nt8Logo from "../images/ori3nt8_long_white.svg";

const Navbar = () => (
  <nav className="navbar is-primary">
    <div className="container">
      <div className="navbar-brand">
        <a className="navbar-item" href="/">
          <img src={ori3nt8Logo} alt="Ori3nt8 logo" />
        </a>
      </div>
      <div className="navbar-menu">
        <div className="navbar-end">
          <span className="navbar-item">
            <a
              className="button is-secondary is-inverted"
              href="https://github.com/nickguletskii/ori3nt8/releases"
            >
              <span className="icon">
                <FaDownload size={32} />
              </span>
              <span>Download</span>
            </a>
          </span>
        </div>
      </div>
    </div>
  </nav>
);

export default Navbar;
