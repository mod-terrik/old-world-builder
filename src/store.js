import { configureStore } from "@reduxjs/toolkit";

import listsReducer from "./state/lists";
import armyReducer from "./state/army";
import itemsReducer from "./state/items";
import errorsReducer from "./state/errors";
import rulesIndexReducer from "./state/rules-index";
import settingsReducer from "./state/settings";

const loadState = () => {
  try {
    const lists = localStorage.getItem("owb.lists");
    const settings = localStorage.getItem("owb.settings");
    const army = localStorage.getItem("owb.army");
    return {
      lists: lists ? JSON.parse(lists) : [],
      settings: settings ? JSON.parse(settings) : undefined,
      army: army ? JSON.parse(army) : null,
    };
  } catch {
    return undefined;
  }
};

const saveState = (state) => {
  try {
    localStorage.setItem("owb.lists", JSON.stringify(state.lists));
    localStorage.setItem("owb.settings", JSON.stringify(state.settings));
    if (state.army) {
      localStorage.setItem("owb.army", JSON.stringify(state.army));
    }
  } catch {
    // ignore write errors
  }
};

const store = configureStore({
  reducer: {
    lists: listsReducer,
    army: armyReducer,
    items: itemsReducer,
    errors: errorsReducer,
    rulesIndex: rulesIndexReducer,
    settings: settingsReducer,
  },
  preloadedState: loadState(),
});

store.subscribe(() => saveState(store.getState()));

export default store;
