import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useParams } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import classNames from "classnames";

import { Dialog } from "../../components/dialog";
import { Spinner } from "../../components/spinner";
import { normalizeRuleName } from "../../utils/string";
import { closeRulesIndex } from "../../state/rules-index";

import { rulesMap, synonyms } from "./rules-map";
import "./RulesIndex.css";

export const RulesIndex = () => {
  const { open, activeRule } = useSelector((state) => state.rulesIndex);
  const [isLoading, setIsLoading] = useState(true);
  const { listId } = useParams();
  const list = useSelector((state) =>
    state.lists.find(({ id }) => listId === id)
  );
  const listArmyComposition = list?.armyComposition || list?.army;
  const dispatch = useDispatch();
  
  const handleClose = () => {
    setIsLoading(true);
    dispatch(closeRulesIndex());
  };
  
  const isRenegadeArmy = listArmyComposition?.includes("renegade");
  const normalizedName =
    activeRule.includes("renegade") && isRenegadeArmy
      ? normalizeRuleName(activeRule)
      : normalizeRuleName(activeRule.replace(" {renegade}", ""));  
  const synonym = synonyms[normalizedName];
  const ruleData = rulesMap[normalizedName] || rulesMap[synonym];
  const rulePath = ruleData?.url;

    //Check if this is a full URL or a relative path
  const iframeUrl = ruleData?.isFullUrl
    ? rulePath  // Use the full URL directly
    : `https://tow.whfb.app/${rulePath}?minimal=true&utm_source=owb&utm_medium=referral`;

      React.useEffect(() => {
    if (open && ruleData?.isFullUrl && rulePath) {
      window.open(rulePath, '_blank', 'noopener,noreferrer');
      handleClose();
    }
  }, [open, ruleData?.isFullUrl, rulePath]);

  return (
    <Dialog open={open} onClose={handleClose}>
      {rulePath ? (
        <>
          <iframe
            onLoad={() => setIsLoading(false)}
            className={classNames(
              "rules-index__iframe",
              !isLoading && "rules-index__iframe--show"
            )}
            src={iframeUrl}
            title="Warhammer: The Old World Online Rules Index"
            height="500"
            width="700"
          />
          {isLoading && <Spinner className="rules-index__spinner" />}
        </>
      ) : (
        <p>
          <FormattedMessage id="editor.noRuleFound" />
        </p>
      )}
    </Dialog>
  );
};
