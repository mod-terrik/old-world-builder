import { configureStore } from "@reduxjs/toolkit";

import listsReducer from "./state/lists";
import armyReducer from "./state/army";
import itemsReducer from "./state/items";
import errorsReducer from "./state/errors";
import rulesIndexReducer from "./state/rules-index";
import settingsReducer from "./state/settings";

const STORAGE_KEY = "owb_state";

const loadState = () => {
  try {
    const serialized = localStorage.getItem(STORAGE_KEY);
    if (!serialized) return undefined;
    return JSON.parse(serialized);
  } catch {
    return undefined;
  }
};

const saveState = (state) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      lists: state.lists,
      settings: state.settings,
    }));
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
