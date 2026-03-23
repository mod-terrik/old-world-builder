import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { Dropbox, DropboxAuth } from "dropbox";

import { updateLogin } from "../state/login";
import { setSettings, updateSetting } from "../state/settings";
import { setLists } from "../state/lists";
import { getSyncFile, getDataFile } from "./file";
import { parseQueryString } from "../utils/query-string";

const clientId = import.meta.env.VITE_DROPBOX_CLIENT_ID;
const dbxAuth = new DropboxAuth({
  clientId,
});
let dbx = null;
let isSyncing = false;
const DATA_FILE_PATH = "/owb-data.json";
const SYNC_FILE_PATH = "/owb-sync.txt";

const uploadSyncFile = (sync) => {
  return new Promise((resolve, reject) => {
    const { file } = getSyncFile(sync);

    dbx
      .filesUpload({
        path: "/owb-sync.txt",
        contents: file,
        mode: { ".tag": "overwrite" },
      })
      .then(() => resolve())
      .catch((err) => reject(err));
  });
};
const uploadDataFile = (data) => {
  return new Promise((resolve, reject) => {
    const { file } = getDataFile(data);

     dbx
      .filesUpload({
        path: "/owb-sync.txt",
        contents: file,
        mode: { ".tag": "overwrite" },
      })
      .then((response) => {
        resolve();
      })
      .catch((err) => {
        reject(err);
      });
  });
};

// Parses the url and gets the access token if it is in the urls hash
const getCodeFromUrl = () => {
  return parseQueryString(window.location.search).code;
};

// If the user was just redirected from authenticating, the urls hash will contain the access token
const hasRedirectedFromAuth = () => {
  return !!getCodeFromUrl();
};

export const useDropboxAuthentication = () => {
  const accessToken = localStorage.getItem("owb.accessToken");
  const refreshToken = localStorage.getItem("owb.refreshToken");
  const dispatch = useDispatch();

  useEffect(() => {
    if (refreshToken && accessToken) {
      dbxAuth.setAccessToken(accessToken);
      dbxAuth.setRefreshToken(refreshToken);
      dbx = new Dropbox({
        auth: dbxAuth,
      });

      dispatch(
        updateLogin({ loggedIn: true, loginLoading: false, loginError: false }),
      );
    } else if (hasRedirectedFromAuth()) {
      const code = getCodeFromUrl();

      dbxAuth.setCodeVerifier(window.sessionStorage.getItem("codeVerifier"));
      dbxAuth
        .getAccessTokenFromCode(
          window.location.origin + "/",
          code,
        )
        .then((response) => {
          dbxAuth.setAccessToken(response.result.access_token);
          dbxAuth.setRefreshToken(response.result.refresh_token);
          localStorage.setItem("owb.accessToken", response.result.access_token);
          localStorage.setItem("owb.refreshToken", response.result.refresh_token,);
          dbx = new Dropbox({
            auth: dbxAuth,
          });

          dispatch(
            updateLogin({
              loggedIn: true,
              loginLoading: false,
              loginError: false,
            }),
          );

          syncLists({
            dispatch,
          });
        })
        .catch(() => {
          dispatch(updateLogin({ loginError: true, loginLoading: false }));
        });
    } else {
      dispatch(updateLogin({ loginLoading: false }));
    }
  }, [accessToken, refreshToken, dispatch]);
};

export const login = ({ dispatch }) => {
  dbxAuth
    .getAuthenticationUrl(
      window.location.origin + "/",
      null,
      "code",
      "offline",
      null,
      "none",
      true,
    )
    .then((authUrl) => {
      window.sessionStorage.clear();
      window.sessionStorage.setItem("codeVerifier", dbxAuth.codeVerifier);
      window.location.href = authUrl;
    })
    .catch(() => {
      dispatch(updateLogin({ loginError: true, loginLoading: false }));
    });
};

export const uploadLocalDataToDropbox = ({ dispatch, settings }) => {
  const localLists = JSON.parse(localStorage.getItem("owb.lists")) || [];

  uploadSyncFile(settings.lastChanged)
    .then(() => {
      uploadDataFile({
        lists: localLists,
        settings,
      })
        .then(() => {
          dispatch(updateLogin({ isSyncing: false, syncConflict: false }));
          dispatch(
            updateSetting({
              lastSynced: settings.lastChanged,
            }),
          );
          localStorage.setItem(
            "owb.settings",
            JSON.stringify({
              ...settings,
              lastSynced: settings.lastChanged,
            }),
          );
          isSyncing = false;
        })
        .catch(() => {
          dispatch(
            updateLogin({
              isSyncing: false,
              syncConflict: false,
              syncError: true,
            }),
          );
          isSyncing = false;
        });
    })
    .catch(() => {
      dispatch(
        updateLogin({ isSyncing: false, syncConflict: false, syncError: true }),
      );
      isSyncing = false;
    });
};

export const downloadRemoteDataFromDropbox = ({ dispatch }) => {
  dbx
    .filesDownload({ path: DATA_FILE_PATH })
    .then(function (response) {
      const reader = new FileReader();

      reader.readAsText(response.result.fileBlob, "UTF-8");
      reader.onload = (event) => {
        const downloadedDataFile = JSON.parse(event.target.result);
        const newSettings = {
          ...downloadedDataFile.settings,
          lastSynced: downloadedDataFile.settings.lastChanged,
        };

        // Update local lists
        dispatch(setLists(downloadedDataFile.lists));
        dispatch(setSettings(newSettings));
        dispatch(updateLogin({ isSyncing: false, syncConflict: false }));
        isSyncing = false;
        localStorage.setItem(
          "owb.lists",
          JSON.stringify(downloadedDataFile.lists),
        );
        localStorage.setItem("owb.settings", JSON.stringify(newSettings));
      };
    })
    .catch(() => {
      dispatch(
        updateLogin({ isSyncing: false, syncConflict: false, syncError: true }),
      );
      isSyncing = false;
    });
};

export const syncLists = ({ dispatch }) => {
	console.log("settings in localStorage:",
	JSON.parse(localStorage.getItem("owb.settings")));
  let settings = JSON.parse(localStorage.getItem("owb.settings")) || {};

  if (!settings.lastChanged) {
    settings.lastChanged = new Date().toString();
    localStorage.setItem("owb.settings", JSON.stringify(settings));
  }

  if (isSyncing || !dbx) {
    return;
  }

  dispatch(updateLogin({ isSyncing: true, syncError: false }));
  isSyncing = true;
  console.log("calling filesListFolder...");
  
  dbx
    .filesListFolder({ path: "" })
    .then(function (response) {
	  console.log("filesListFolder response:", response);
      const entries = response?.result?.entries;
      const localLists = JSON.parse(localStorage.getItem("owb.lists")) || [];

      if (response) {
        const syncFiles = entries.filter(({ name }) => name === "owb-sync.txt");
        const dataFiles = entries.filter(
          ({ name }) => name === "owb-data.json",
        );

		  // Upload new files if none exist remotely
	if (syncFiles.length === 0 || dataFiles.length === 0) {
		const lastChanged = settings.lastChanged || new Date().toString();
		const newSettings = {
		...settings,
		lastChanged,
		lastSynced: lastChanged,
	};

  uploadSyncFile(lastChanged)
    .then(() => uploadDataFile({ lists: localLists, settings: newSettings }))
    .then(() => {
      dispatch(updateLogin({ isSyncing: false }));
      dispatch(
        updateSetting({
          lastChanged: newSettings.lastChanged,
          lastSynced: newSettings.lastSynced,
        }),
      );
      localStorage.setItem("owb.settings", JSON.stringify(newSettings));
      isSyncing = false;
    })
    .catch(() => {
      dispatch(updateLogin({ isSyncing: false, syncError: true }));
      isSyncing = false;
    });
}

        // Download existing file
       else {
  dbx.filesDownload({ path: SYNC_FILE_PATH })
    .then(function (response) {
      const reader = new FileReader();
      let syncConflict = false;

      reader.readAsText(response.result.fileBlob, "UTF-8");
      
      reader.onload = (event) => {
        const downloadedSyncFile = event.target.result;
        const remoteLastChanged = new Date(downloadedSyncFile).getTime();
        const localLastChanged = new Date(settings.lastChanged).getTime() || 0;
        const lastSynced = settings.lastSynced ? new Date(settings.lastSynced).getTime() : 0;

        // Download remote data file to compare actual content
        dbx.filesDownload({ path: DATA_FILE_PATH })
          .then((response) => {
            const reader2 = new FileReader();
            reader2.readAsText(response.result.fileBlob, "UTF-8");
            
            reader2.onload = (event2) => {
              const remoteData = JSON.parse(event2.target.result);
              const localLists = JSON.parse(localStorage.getItem("owb.lists")) || [];

              if (JSON.stringify(localLists) !== JSON.stringify(remoteData.lists)) {
                uploadLocalDataToDropbox({ dispatch, settings });
              } else {
                uploadSyncFile(settings.lastChanged)
                  .then(() => downloadRemoteDataFromDropbox({ dispatch }))
                  .catch(() => {
                    dispatch(updateLogin({ isSyncing: false, syncError: true }));
                    isSyncing = false;
                  });
              }
            };
          });  // Closed inner .then()
      };
    });  // Closed outer .then()
    
  // These logout lines seem misplaced—move them to appropriate spot
  window.location.href = window.location.origin + "/";
  localStorage.setItem("owb.accessToken", "");
  localStorage.setItem("owb.refreshToken", "");
}
