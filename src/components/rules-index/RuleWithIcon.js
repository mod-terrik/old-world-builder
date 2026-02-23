import { useDispatch } from "react-redux";
import { useIntl } from "react-intl";
import PropTypes from "prop-types";
import classNames from "classnames";

import { Button } from "../button";
import { normalizeRuleName } from "../../utils/string";
import { openRulesIndex } from "../../state/rules-index";

import { rulesMap, synonyms } from "./rules-map";
import "./RuleWithIcon.css";

const getLocalHref = (unitSlug) => {
  if (!unitSlug) return null;
  const local = LOCAL_UNIT_REDIRECTS[unitSlug];
  if (!local) return null;
  return local;
};

export const RuleWithIcon = ({ name, unitSlug, isDark, className }) => {
  const dispatch = useDispatch();
  const intl = useIntl();

  if (!name && !unitSlug) {
    return null;
  }

  const localHref = getLocalHref(unitSlug);

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

