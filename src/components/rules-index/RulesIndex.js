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
  const compNote = ruleData?.compNote;

  // Check if this is a full URL or a relative path
  const iframeUrl = ruleData?.isFullUrl
    ? rulePath  // Use the full URL directly
    : `https://tow.whfb.app/${rulePath}?minimal=true&utm_source=owb&utm_medium=referral`;

  React.useEffect(() => {
    if (open && ruleData?.isFullUrl && rulePath) {
      window.open(rulePath, '_blank', 'noopener,noreferrer');
      handleClose();
    }
  }, [open, ruleData?.isFullUrl, rulePath]);

  // Get display name for the rule (remove tags like {renegade})
  const displayRuleName = activeRule.replace(/ *\{[^)]*\}/g, "");

  return (
    <Dialog open={open} onClose={handleClose}>
      {rulePath ? (
        <>
          {compNote && (
            <div className="rules-index__comp-note" style={{
              padding: "12px",
              backgroundColor: "#f5f5f5",
              borderBottom: "1px solid #ddd",
              marginBottom: "8px"
            }}>
		<p style={{ margin: "0 0 8px 0" }}>
  		<span className="rules-index__comp-note-title">{displayRuleName}</span>
		</p>   
              <p style={{ margin: 0, fontSize: "18px" }}>
                {compNote}
              </p>
            </div>
          )}
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
      ) : compNote ? (
        <div style={{ padding: "20px" }}>
           <span className="rules-index__comp-note-title" style={{ display: "block", margin: "0 0 12px 0" }}>
	   {displayRuleName}
           </span>
          <p style={{ margin: 0, fontSize: "14px" }}>
            {compNote}
          </p>
        </div>
      ) : (
        <p>
          <FormattedMessage id="editor.noRuleFound" />
        </p>
      )}
    </Dialog>
  );
};

