import { useDispatch } from "react-redux";
import { useIntl } from "react-intl";
import PropTypes from "prop-types";
import classNames from "classnames";

import { Button } from "../button";
import { normalizeRuleName } from "../../utils/string";
import { openRulesIndex } from "../../state/rules-index";

import { rulesMap, synonyms } from "./rules-map";
import "./RuleWithIcon.css";

// ============================================================
// ADD LOCAL UNIT REDIRECTS HERE
// Format: "unit-slug": "/local/path"
// The path will be prefixed with PUBLIC_URL automatically.
// ============================================================
const LOCAL_UNIT_REDIRECTS = {
  "gnoblar-scraplauncher": "unit/gnoblar-scraplauncher",
  // "iron-blaster": "/rules/unit/iron-blaster",
  // "mournfang-pack": "/rules/unit/mournfang-pack",
};
// ============================================================

const getLocalHref = (unitSlug) => {
  if (!unitSlug) return null;
  const local = LOCAL_UNIT_REDIRECTS[unitSlug];
  if (!local) return null;
  return `${process.env.PUBLIC_URL || ""}${local}`;
};

export const RuleWithIcon = ({ name, unitSlug, isDark, className }) => {
  const dispatch = useDispatch();
  const intl = useIntl();

  if (!name && !unitSlug) {
    return null;
  }

  const localHref = getLocalHref(unitSlug);

  if (localHref) {
    return (
      <a
        href={localHref}
        target="_blank"
        rel="noopener noreferrer"
        className={classNames("rule-icon", className && className)}
        aria-label={intl.formatMessage({ id: "misc.showRules" })}
      >
        <Button
          type="text"
          color={isDark ? "dark" : "light"}
          label={intl.formatMessage({ id: "misc.showRules" })}
          icon="preview"
          tabIndex={-1}
        />
      </a>
    );
  }

  const normalizedName = normalizeRuleName(name);
  const synonym = synonyms[normalizedName];

  return rulesMap[normalizedName] || rulesMap[synonym] ? (
    <Button
      type="text"
      className={classNames("rule-icon", className && className)}
      color={isDark ? "dark" : "light"}
      label={intl.formatMessage({ id: "misc.showRules" })}
      icon="preview"
      onClick={() => dispatch(openRulesIndex({ activeRule: name }))}
    />
  ) : null;
};

RuleWithIcon.propTypes = {
  className: PropTypes.string,
  name: PropTypes.string,
  unitSlug: PropTypes.string,
  isDark: PropTypes.bool,
};

