import React, { useState, useRef, useEffect } from "react";
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
  const iframeRef = useRef(null);
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
  
  const normalizedName =
    activeRule.includes("renegade") && listArmyComposition?.includes("renegade")
      ? normalizeRuleName(activeRule)
      : normalizeRuleName(activeRule.replace(" {renegade}", ""));
  const synonym = synonyms[normalizedName];
  const ruleData = rulesMap[normalizedName] || rulesMap[synonym];
  const rulePath = ruleData?.fullUrl || (ruleData?.url ? `https://tow.whfb.app/${ruleData.url}?minimal=true&utm_source=owb&utm_medium=referral` : null);

  // Inject script into iframe to handle link clicks and add minimal=true
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe || !open) return;

    const handleIframeLoad = () => {
      setIsLoading(false);
      
      try {
        // Try to inject script into iframe (will only work for same-origin)
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        
        if (iframeDoc) {
          // Inject script to intercept link clicks and add minimal=true
          const script = iframeDoc.createElement('script');
          script.textContent = `
            (function() {
              // Function to ensure minimal parameter exists
              function ensureMinimalParam(url) {
                try {
                  const urlObj = new URL(url, window.location.href);
                  
                  // Only modify tow.whfb.app URLs
                  if (urlObj.hostname === 'tow.whfb.app' || urlObj.hostname === window.location.hostname) {
                    if (!urlObj.searchParams.has('minimal')) {
                      urlObj.searchParams.set('minimal', 'true');
                    }
                  }
                  
                  return urlObj.toString();
                } catch (e) {
                  return url;
                }
              }
              
              // Intercept all link clicks
              document.addEventListener('click', function(e) {
                const link = e.target.closest('a');
                if (link && link.href) {
                  const newHref = ensureMinimalParam(link.href);
                  if (newHref !== link.href) {
                    e.preventDefault();
                    window.location.href = newHref;
                  }
                }
              }, true);
              
              // Also modify existing links on page load
              document.querySelectorAll('a[href]').forEach(function(link) {
                const href = link.getAttribute('href');
                if (href && (href.startsWith('http') || href.startsWith('/'))) {
                  const newHref = ensureMinimalParam(link.href);
                  if (newHref !== link.href) {
                    link.href = newHref;
                  }
                }
              });
            })();
          `;
          
          // Only inject if not already injected
          if (!iframeDoc.querySelector('script[data-minimal-interceptor]')) {
            script.setAttribute('data-minimal-interceptor', 'true');
            iframeDoc.body?.appendChild(script);
          }
        }
      } catch (e) {
        // Cross-origin restriction - expected for external tow.whfb.app pages
        // The minimal parameter should already be in the initial URL
        console.log('Cannot inject script into cross-origin iframe');
      }
    };

    iframe.addEventListener('load', handleIframeLoad);
    
    return () => {
      iframe.removeEventListener('load', handleIframeLoad);
    };
  }, [open]);

  return (
    <Dialog open={open} onClose={handleClose}>
      {rulePath ? (
        <>
          <iframe
            ref={iframeRef}
            onLoad={() => setIsLoading(false)}
            className={classNames(
              "rules-index__iframe",
              !isLoading && "rules-index__iframe--show"
            )}
            src={rulePath}
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
