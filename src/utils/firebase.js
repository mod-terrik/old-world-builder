import { initializeApp } from "firebase/app";
import { getFirestore, doc, setDoc, getDoc } from "firebase/firestore";
import { getAuth, signInAnonymously } from "firebase/auth";

const firebaseConfig = {
  // Paste your Firebase project config here
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);

export const getOrCreateSyncId = async () => {
  let syncId = localStorage.getItem("owb.syncId");
  if (!syncId) {
    await signInAnonymously(auth);
    syncId = auth.currentUser.uid;
    localStorage.setItem("owb.syncId", syncId);
  }
  return syncId;
};

export const pushLists = async (lists) => {
  const syncId = await getOrCreateSyncId();
  await setDoc(doc(db, "armylists", syncId), { lists });
};

export const pullLists = async () => {
  const syncId = localStorage.getItem("owb.syncId");
  if (!syncId) return null;
  const snap = await getDoc(doc(db, "armylists", syncId));
  return snap.exists() ? snap.data().lists : null;
};
