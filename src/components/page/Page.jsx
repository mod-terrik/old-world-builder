import React from "react";
import classNames from "classnames";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { FormattedMessage } from "react-intl";

import { Spinner } from "../../components/spinner";

import "./Page.css";

export const Main = ({ className, children, isDesktop, compact, loading }) => {
  const handleLanguageChange = (event) => {
    localStorage.setItem("lang", event.target.value);
    window.location.reload();
  };

  return (
    <>
      <main
        className={classNames(
          "main",
          isDesktop ? "main--desktop" : "main--mobile",
          compact && "main--compact",
          className
        )}
      >
        {children}
        {loading && <Spinner />}
      </main>
      {!loading && (
        <footer className="footer">
          <nav className="footer__navigation">
            <Link to="/about">
              <FormattedMessage id="footer.about" />
            </Link>
          </nav>
        </footer>
      )}
    </>
  );
};

Main.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node,
  isDesktop: PropTypes.bool,
};
