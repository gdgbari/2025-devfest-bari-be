import { Group } from "@models/Group";
import { UserProfile } from "@models/UserProfile";
import { GenericResponse } from "@modelsresponse/GenericResponse";
import * as admin from "firebase-admin";
import { getAuth } from "firebase-admin/auth";
import * as functions from "firebase-functions";
import { db } from "../index";
import { parseGroupRef } from "../utils/firestoreHelpers";
import { serializedErrorResponse, serializedExceptionResponse, serializedSuccessResponse } from "../utils/responseHelper";

export const signUp = functions.https.onCall(async (data, context) => {
    const { name, surname, nickname, email, password } = data;

    try {
        const userRecord = await getAuth()
            .createUser({
                email: email,
                emailVerified: true,
                password: password,
                displayName: name + ' ' + surname,
                disabled: false,
            });

        const uid = userRecord.uid;

        const usersRef = db.collection("users");

        const userDoc = await usersRef.doc(uid).get();

        if (userDoc.exists) {
            return serializedErrorResponse("user-already-registered", "The user is already registered.");
        }

        usersRef.doc(uid).set({
            name: name,
            surname: surname,
            email: email,
            nickname: nickname,
            group: null,
            role: "attendee"
        });

        // Initialize the user's score to 0
        await admin.database()
            .ref(`leaderboard/users/${uid}`)
            .set({
                groupColor: 'black',
                nickname: nickname,
                score: 0,
                timestamp: Date.now()
            });

        return serializedSuccessResponse(uid);
    } catch (error) {
        console.error("An error occurred while registering the user.", error);
        return serializedExceptionResponse(error);
    }
});

export const getUserProfile = functions.https.onCall(async (_, context) => {

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
    }

    try {
        const userDoc = await db.collection("users").doc(context.auth.uid).get();

        if (!userDoc.exists) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        const userData = userDoc.data();

        if (!userData) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        var group: Group | null = null;

        if (userData.group != null) {
            const groupResponse: GenericResponse<Group> = await parseGroupRef(userData.group);

            if (groupResponse.error) {
                return serializedErrorResponse(groupResponse.error.errorCode, groupResponse.error.details);
            }

            group = groupResponse.data as Group;
        }

        const userProfile: UserProfile = {
            userId: userDoc.id,
            nickname: userData.nickname,
            email: userData.email,
            name: userData.name,
            surname: userData.surname,
            group: group,
            groupId: group ? group.groupId : null,
            position: null,
            score: userData.score,
            role: userData.role
        };

        return serializedSuccessResponse(userProfile);
    } catch (error) {
        console.error("An error occurred while fetching the user profile.", error);
        return serializedExceptionResponse(error);
    }
});

export const getUserProfileById = functions.https.onCall(async (data, context) => {

    const { userId } = data;

    if (!context.auth?.uid) {
        return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
    }

    const userDoc = await db.collection("users").doc(context.auth.uid).get();

    if (!userDoc.exists) {
        return serializedErrorResponse("user-not-found", "User not found.");
    }

    const userData = userDoc.data();

    if (!userData) {
        return serializedErrorResponse("user-not-found", "User data not found.");
    }

    if (userData.role != "staff") {
        return serializedErrorResponse("permission-denied", "User not authorized.");
    }


    try {
        const userDoc = await db.collection("users").doc(userId).get();

        if (!userDoc.exists) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        const userData = userDoc.data();

        if (!userData) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        var group: Group | null = null;

        if (userData.group != null) {
            const groupResponse: GenericResponse<Group> = await parseGroupRef(userData.group);

            if (groupResponse.error) {
                return serializedErrorResponse(groupResponse.error.errorCode, groupResponse.error.details);
            }

            group = groupResponse.data as Group;
        }

        const userProfile: UserProfile = {
            userId: userDoc.id,
            nickname: userData.nickname,
            email: userData.email,
            name: userData.name,
            surname: userData.surname,
            group: group,
            groupId: group ? group.groupId : null,
            position: null,
            score: userData.score,
            role: userData.role
        };

        return serializedSuccessResponse(userProfile);
    } catch (error) {
        console.error("An error occurred while fetching the user profile.", error);
        return serializedExceptionResponse(error);
    }

});


export const redeemAuthCode = functions.https.onCall(async (data, context) => {
    const { code } = data;

    if (!context.auth?.uid) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    if (!code.startsWith("checkin:")) {
        return serializedErrorResponse("invalid-code", "The code is not a valid check-in code.");
    }

    try {
        const codeParts = code.split(":");
        const codeId = codeParts[codeParts.length - 1];
        const authCodeDoc = await db.collection("authorizationCodes").doc(codeId).get();

        if (!authCodeDoc.exists) {
            return serializedErrorResponse("code-not-found", "The authorization code does not exist.");
        }

        const authCodeData = authCodeDoc.data();
        const userReference = db.collection("users").doc(context.auth.uid);

        if (authCodeData?.expired) {
            return serializedErrorResponse("code-expired", "The authorization code has expired.");
        }

        const groupReference = authCodeData?.group;

        await db.collection("users").doc(context.auth.uid).set({
            group: groupReference,
        }, { merge: true });

        await db.collection("authorizationCodes").doc(codeId).set({
            expired: true,
            user: userReference,
        }, { merge: true });

        const group = (await parseGroupRef(groupReference)).data as Group;
        const userDoc = await userReference.get();
        const userData = userDoc.data();
        if (!userData) {
            return serializedErrorResponse("user-not-found", "User data not found.");
        }

        // set group color in leaderboard's user
        await admin.database()
            .ref(`leaderboard/users/${context.auth.uid}`)
            .update({ groupColor: group.color });

        return serializedSuccessResponse(group);
    } catch (error) {
        console.error("An error occurred while redeeming the authorization code.", error);
        return serializedExceptionResponse(error);
    }
});
