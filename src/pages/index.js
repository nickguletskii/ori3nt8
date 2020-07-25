import "../components/style.scss";
import React from "react";
import Layout from "../components/layout";
import { FaGithub, FaDownload } from "react-icons/fa";
import Navbar from "../components/navbar";
import ori3nt8Screenshot from "../images/ori3nt8_screenshot.png";

const IndexPage = () => (
  <Layout includeNavbar={false}>
    <section className="hero primary-hero is-fullheight-with-navbar">
      <div className="hero-head">
        <Navbar />
      </div>
      <div className="hero-body">
        <div className="container">
          <article className="media">
            <div className="media-content">
              <div className="content">
                <figure class="image is-4x3">
                  <img src={ori3nt8Screenshot} alt="A screenshot of Ori3nt8" />
                </figure>
                <h1 className="is-uppercase is-size-1 has-text-white has-text-centered">
                  Fix rotated photos in a breeze
                </h1>
                <p className="subtitle has-text-white is-size-3 has-text-centered">
                  Automatically rotate your photos while viewing them
                </p>
                <p className="has-text-white has-text-centered">
                  Ori3nt8 is a program that tries to automatically guess the
                  correct orientation of your photos using a neural network and
                  rotates them by correcting their EXIF metadata.
                </p>
                <p className="has-text-white has-text-centered">
                  <a
                    className="button is-secondary is-inverted is-large"
                    href="https://github.com/nickguletskii/ori3nt8/releases"
                  >
                    <span className="icon">
                      <FaDownload size="fa-2x" />
                    </span>
                    <span>Download</span>
                  </a>{" "}
                  <a
                    className="button is-secondary is-inverted is-large"
                    href="https://github.com/nickguletskii/ori3nt8"
                  >
                    <span className="icon">
                      <FaGithub size="fa-2x" />
                    </span>
                    <span>Source code</span>
                  </a>
                </p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section className="section">
      <div className="container">
        <h1 className="title">How do I use it?</h1>
        <h2 className="subtitle">
          <ol>
            <li>
              Open a directory by pressing Ctrl + O, or selecting File &gt; Open
              Directory.
            </li>
            <li>
              Select a photo in the file tree on the right. Only JPEG files are
              currently supported.
            </li>
            <li>
              The original orientation of the photo is indicated using a yellow
              rectangle. After a second or two, a green triangle should appear
              and the photo will be rotated automatically. The green triangle
              indicates the suggested orientation for this image. The
              orientation will be saved automatically.
            </li>
            <li>
              Move on to the next photo by pressing the right arrow on your
              keyboard. To select the previous photo, press the left arrow.
            </li>
            <li>
              You may disable automatic rotation by unchecking Edit &gt;
              Automatically apply suggested orientation. After automatic
              rotation has been disabled, you may apply the suggested rotation
              by clicking "Apply" or pressing the spacebar.
            </li>
            <li>
              The image can be rotated clockwise by pressing D or
              counter-clockwise by pressing A.
            </li>
          </ol>
        </h2>
      </div>
    </section>
  </Layout>
);

export default IndexPage;
