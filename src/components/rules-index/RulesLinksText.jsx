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
    // Remove {renegade} tag from the rule name for normalization
    const cleanedRuleEn = textEn[index].replace(/ *\{[^)]*\}/g, "");
    const normalizedName = normalizeRuleName(cleanedRuleEn);
    const renegadeName = isRenegade
      ? normalizeRuleName(`${cleanedRuleEn} renegade`)
      : null;
    const synonym = synonyms[normalizedName];
    
    // Try to find the rule in this order:
    // 1. Renegade version (if isRenegade is true)
    // 2. Synonym version
    // 3. Regular version
    const ruleData =
      (renegadeName && rulesMap[renegadeName]) ||
      rulesMap[synonym || normalizedName];
    
    // Determine which rule name to use when opening the rules index
    const activeRuleName =
      renegadeName && rulesMap[renegadeName]
        ? `${cleanedRuleEn} renegade`
        : cleanedRuleEn;

    return (
      <Fragment key={`${rule}-${index}`}>
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
            {rule.replace(/ *\{[^)]*\}/g, "")}
            {index !== ruleButtons.length - 1 && ", "}
          </>
        )}
      </Fragment>
    );
  });
};

