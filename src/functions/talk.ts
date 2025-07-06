import * as functions from "firebase-functions";
import { Timestamp } from "firebase-admin/firestore";
import { db } from "../index";
import { Talk } from "@models/Talk";
import { serializedErrorResponse, serializedSuccessResponse, serializedExceptionResponse } from "../utils/responseHelper";

export const createTalk = functions.https.onCall(async (data, context) => {
    const { title, description, track, room, startTime, endTime } = data;

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

        if (userData.role != "staff") {
            return serializedErrorResponse("permission-denied", "User not authorized.");
        }

        const talksRef = db.collection("talks");

        const talkDoc = await talksRef.add({
            title: title ?? "",
            description: description ?? "",
            track: track ?? "",
            room: room ?? "",
            startTime: Timestamp.fromMillis(startTime ?? 0),
            endTime: Timestamp.fromMillis(endTime ?? 0),
        });

        return serializedSuccessResponse({ talkId: talkDoc.id });
    } catch (error) {
        console.error("An error occurred while creating the talk.", error);
        return serializedExceptionResponse(error);
    }
});

export const getTalkList = functions.https.onCall(async (_, context) => {
    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
    }

    try {
        const talksSnapshot = await db.collection("talks").get();

        if (!talksSnapshot) {
            return serializedErrorResponse("talks-not-found", "No talks found.");
        }

        const talkList = await Promise.all(
            talksSnapshot.docs.map(async (talkDoc) => {
                const talkData = talkDoc.data();

                const talk: Talk = {
                    talkId: talkDoc.id,
                    title: talkData.title,
                    description: talkData.description,
                    track: talkData.track,
                    room: talkData.room,
                    startTime: talkData.startTime.toMillis(),
                    endTime: talkData.endTime.toMillis(),
                };

                return talk;
            })
        );

        return serializedSuccessResponse(talkList);
    } catch (error) {
        console.error("An error occurred while fetching the talk list.", error);
        return serializedExceptionResponse(error);
    }
});
