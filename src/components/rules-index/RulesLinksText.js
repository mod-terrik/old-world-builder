import { Fragment } from "react";
import { useDispatch } from "react-redux";

import { normalizeRuleName } from "../../utils/string";
import { useLanguage } from "../../utils/useLanguage";
import { openRulesIndex } from "../../state/rules-index";

import { rulesMap, synonyms } from "./rules-map";

export const RulesLinksText = ({ textObject, showPageNumbers, isRenegade }) => {
  const dispatch = useDispatch();
  const { language } = useLanguage();

  if (!textObject?.name_en) {
    return [];
  }

  const textEn = textObject.name_en.split(", ");
  const ruleString = textObject[`name_${language}`] || textObject.name_en;
  let ruleButtons = ruleString.split(", ");

  return ruleButtons.map((rule, index) => {
    const normalizedName = normalizeRuleName(textEn[index]);
    const renegadeName = isRenegade
      ? normalizeRuleName(`${textEn[index]} renegade`)
      : null;
    const synonym = synonyms[normalizedName];
    const ruleData =
      (renegadeName && rulesMap[renegadeName]) ||
      rulesMap[synonym || normalizedName];
    const activeRuleName =
      renegadeName && rulesMap[renegadeName]
        ? `${textEn[index]} renegade`
        : textEn[index];

    return (
      <Fragment key={rule}>
        {ruleData ? (
          <>
            <button
              className="unit__rule"
              onClick={() =>
                dispatch(openRulesIndex({ activeRule: activeRuleName }))
              }
            >
              {rule.replace(/ *\{[^)]*\}/g, "")}
            </button>
            {showPageNumbers && ` [${ruleData.page}]`}
            {index !== ruleButtons.length - 1 && ", "}
          </>
        ) : (
          <>
            {rule}
            {index !== ruleButtons.length - 1 && ", "}
          </>
        )}
      </Fragment>
    );
  });
};
