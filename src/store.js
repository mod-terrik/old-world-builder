import { configureStore } from "@reduxjs/toolkit";

import listsReducer from "./state/lists";
import armyReducer from "./state/army";
import itemsReducer from "./state/items";
import errorsReducer from "./state/errors";
import rulesIndexReducer from "./state/rules-index";
import settingsReducer from "./state/settings";

const saveState = (state) => {
  try {
    localStorage.setItem("owb.lists", JSON.stringify(state.lists));
    localStorage.setItem("owb.settings", JSON.stringify(state.settings));
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
});

store.subscribe(() => saveState(store.getState()));

export default store;
