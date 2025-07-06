require("module-alias/register");

import * as admin from "firebase-admin";
import { getUserProfile, signUp, redeemAuthCode, getUserProfileById } from "./functions/auth";
import { createTalk, getTalkList } from "./functions/talk";
import { getSponsorList } from "./functions/sponsor";
import { getLeaderboard, refreshLeaderboard } from "./functions/leaderboard";
import {
    getQuizHistory,
    getQuiz,
    createQuiz,
    submitQuiz,
    deleteQuiz,
    getQuizList,
    addPointsToUsers,
    toggleIsOpen,
} from "./functions/quiz";

admin.initializeApp();
export const db = admin.firestore();

export {
    signUp,
    getUserProfile,
    createTalk,
    getTalkList,
    getSponsorList,
    getQuizHistory,
    getQuiz,
    createQuiz,
    submitQuiz,
    deleteQuiz,
    getQuizList,
    getLeaderboard,
    refreshLeaderboard,
    redeemAuthCode,
    addPointsToUsers,
    getUserProfileById,
    toggleIsOpen,
};
