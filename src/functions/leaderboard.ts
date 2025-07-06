import * as functions from "firebase-functions";
import {serializedSuccessResponse, serializedErrorResponse, serializedExceptionResponse} from "../utils/responseHelper";
import {db} from "../index";
import {Leaderboard} from "@modelsLeaderboard";
import {Group} from "@modelsGroup";
import {QuizResult} from "@modelsQuizResult";
import {GenericResponse} from "@modelsresponse/GenericResponse";
import {parseGroupRef} from "../utils/firestoreHelpers";
import {LeaderboardUserEntry} from "@modelsLeaderboardUserEntry";

export const getLeaderboard = functions.https.onCall(async (_, context) => {
    try {
        if (!context.auth) {
            return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
        }

        const userDoc = await db.collection("users").doc(context.auth.uid).get();

        if (!userDoc.exists) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        const userData = userDoc.data();

        if (!userData) {
            return serializedErrorResponse("user-not-found", "The user does not exist.");
        }

        // if (userData.role != "staff") {
        //     return serializedErrorResponse("permission-denied", "User not authorized.");
        // }

        const usersSnapshot = await db.collection("users").get();

        if (!usersSnapshot) {
            return serializedErrorResponse("users-not-found", "No user found.");
        }

        const users =
            await Promise.all(
                usersSnapshot.docs.filter(userDoc =>
                    userDoc.data().group != null
                ).map(async (userDoc) => {
                    const userData = userDoc.data();
                    const groupColor: string = await parseGroupRef(userData.group)
                        .then((groupResponse: GenericResponse<Group>) => {
                            const groupData = groupResponse.data as Group;
                            return groupData.color;
                        });

                    const entry: LeaderboardUserEntry = {
                        nickname: userData.nickname,
                        position: null,
                        score: userData.score,
                        groupColor: groupColor,
                    }

                    return entry;
                })
            );

        // Sort users by score and set the position
        users.sort((a, b) => {
            return (b.score || 0) - (a.score || 0);
        }).forEach((user, index) => {
            user.position = index + 1;
        });
        const currentUser = users.find(user => user.nickname === userData.nickname);

        const groupsSnapshot = await db.collection("groups").get();

        if (!groupsSnapshot) {
            return serializedErrorResponse("groups-not-found", "No group found.");
        }

        const groups = await Promise.all(
            groupsSnapshot.docs.map(async (groupDoc) => {
                const groupData = groupDoc.data();

                const leaderboardGroupEntry: Group = {
                    groupId: groupDoc.id,
                    name: groupData.name,
                    score: groupData.score,
                    position: null,
                    imageUrl: groupData.imageUrl,
                    color: groupData.color,
                };

                return leaderboardGroupEntry;
            })
        );

        // Sort groups by score and set the position
        groups.sort((a, b) => {
            return (b.score || 0) - (a.score || 0);
        }).forEach((group, index) => {
            group.position = index + 1;
        });

        let leaderboard = {
            currentUser: currentUser || null,
            users: users,
            groups: groups,
        } as Leaderboard;
        return serializedSuccessResponse(leaderboard);
    } catch (error) {
        console.error("An error occurred while fetching the leaderboard.", error);
        return serializedExceptionResponse(error);
    }
});

async function _refreshLeaderboard() {
    try {
        const usersCollection = db.collection("users");
        const groupsCollection = db.collection("groups");

        const usersSnapshot = await usersCollection.get();
        const groupsSnapshot = await groupsCollection.get();
        const groupsScore: { [key: string]: number } = {};

        if (!usersSnapshot) {
            return serializedErrorResponse("users-not-found", "No user found.");
        }
        if (!groupsSnapshot) {
            return serializedErrorResponse("groups-not-found", "No group found.");
        }

        const users = usersSnapshot.docs
            .filter(userDoc => userDoc.data().group != null);
        for (const userDoc of users) {
            let userAcc = 0;
            let userRef = usersCollection.doc(userDoc.id);
            const userData = userDoc.data();

            await userRef
                .collection("quizResults")
                .get()
                .then((quizResultSnapshot) => {
                    quizResultSnapshot.docs.forEach((quizResultDoc) => {
                        const quizResult = quizResultDoc.data() as QuizResult;
                        userAcc += quizResult.score;
                    });

                    parseGroupRef(userData.group).then((groupResponse: GenericResponse<Group>) => {
                        const groupData = groupResponse.data as Group;
                        if (!groupsScore[groupData.groupId]) {
                            groupsScore[groupData.groupId] = 0;
                        }
                        groupsScore[groupData.groupId] += userAcc || 0;
                    });
                });

            await userRef.update({
                score: userAcc
            });
        }


        for (const groupDoc of groupsSnapshot.docs) {
            await groupsCollection.doc(groupDoc.id).update({
                score: groupsScore[groupDoc.id] || 0,
            });
        }

        return;
    } catch (error) {
        console.error("An error occurred while refreshing the leaderboard.", error);
        return serializedExceptionResponse(error);
    }
}

// export const refreshLeaderboardScheduled = functions.pubsub.schedule('every 5 seconds').onRun(async (_) => {
//     return _refreshLeaderboard();
// });

export const refreshLeaderboard = functions.https.onCall(async (_, context) => {
    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "The request has to be authenticated.");
    }

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

    functions.logger.log("Leaderboard refresh requested by ", context.auth.uid);

    return _refreshLeaderboard();
});
