import { Question } from "@models/Question";
import { Quiz } from "@models/Quiz";
import { QuizResult } from "@models/QuizResult";
import { QuizStartTime } from "@models/QuizStartTime";
import { GenericResponse } from "@modelsresponse/GenericResponse";
import * as admin from "firebase-admin";
import { DocumentReference } from "firebase-admin/firestore";
import * as functions from "firebase-functions";
import { db } from "../index";
import { parseGroupRef, parseQuestionListRef } from "../utils/firestoreHelpers";
import { serializedErrorResponse, serializedExceptionResponse, serializedSuccessResponse } from "../utils/responseHelper";
import { generateUniqueRandomStrings } from "../utils/stringHelpers";

const timePerQuestion = 60 * 1000;
const backoffTime = 30 * 1000;

export const createQuiz = functions.https.onCall(async (data, context) => {
    const { questionList, type, title, isOpen } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
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

        const questionListRef: DocumentReference[] = [];
        let maxScore = 0;

        for (const question of questionList) {
            const { text, answerList, correctAnswer, value } = question;

            const answerListIds = generateUniqueRandomStrings(answerList.length);
            const parsedAnswerList = answerList.map((answer: string) => {
                return {
                    id: answerListIds.pop() ?? "",
                    text: answer,
                };
            });

            const parsedCorrectAnswer = parsedAnswerList[correctAnswer].id;

            const questionsRef = db.collection("questions");
            const questionDoc = await questionsRef.add({
                text: text ?? "",
                answerList: parsedAnswerList ?? [],
                correctAnswer: parsedCorrectAnswer,
                value: value ?? 0,
            } as Question);

            questionListRef.push(questionDoc);

            maxScore += value ?? 0;
        }

        // Create the quiz document
        const quizRef = db.collection("quizzes");
        const quizDoc = await quizRef.add({
            questionList: questionListRef,
            type: type,
            title: title ?? "",
            maxScore: maxScore,
            isOpen: isOpen ?? false,
            timerDuration: timePerQuestion * questionList.length,
            creatorUid: context.auth.uid,
        });

        return serializedSuccessResponse({ quizId: quizDoc.id });
    } catch (error) {
        console.error("An error occurred while creating the quiz.", error);
        return serializedExceptionResponse(error);
    }
});


export const getQuiz = functions.https.onCall(async (data, context) => {
    const { code } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    const uid = context.auth.uid;

    if (!code) {
        return serializedErrorResponse("invalid-argument", "The function must be called with a valid quizId.");
    }

    if (!code.startsWith("quiz:")) {
        return serializedErrorResponse("invalid-quiz-code", "The string is not a valid quizId.");
    }

    try {
        const codeParts = code.split(":");
        const quizId = codeParts[codeParts.length - 1];
        const quizDoc = await db.collection("quizzes").doc(quizId).get();

        if (!quizDoc.exists) {
            return serializedErrorResponse("quiz-not-found", "Quiz not found.");
        }

        const quizData = quizDoc.data();

        if (!quizData || !quizData.isOpen) {
            return serializedErrorResponse("quiz-not-open", "Quiz is not open.");
        }

        const questionListResponse: GenericResponse<Question[]> = await parseQuestionListRef(
            quizData.questionList,
            true
        );

        if (questionListResponse.error) {
            return serializedErrorResponse(questionListResponse.error.errorCode, questionListResponse.error.details);
        }

        const questionList: Question[] = questionListResponse.data as Question[];

        const quiz: Quiz = {
            quizId: quizDoc.id,
            title: quizData.title,
            type: quizData.type,
            talkId: null,
            sponsorId: null,
            maxScore: quizData.maxScore,
            isOpen: null,
            questionList: questionList,
            timerDuration: quizData.timerDuration,
            creatorUid: null,
        };

        const answerDoc = await db
            .collection("users")
            .doc(uid)
            .collection("quizResults")
            .doc(quizId)
            .get();

        if (answerDoc.exists) {
            return serializedErrorResponse("quiz-already-submitted", "Quiz already submitted.");
        }

        const startTimeDoc = db
            .collection("users")
            .doc(uid)
            .collection("quizStartTimes")
            .doc(quizId);
        const startTimeDocSnapshot = await startTimeDoc.get();

        if (!startTimeDocSnapshot.exists) {
            const startTime: QuizStartTime = { startTimestamp: Date.now() };
            await startTimeDoc.set(startTime);
        } else {
            const startTimeData = startTimeDocSnapshot.data();

            if (!startTimeData) {
                return serializedErrorResponse("quiz-start-time-not-found", "Quiz start time for user not found.");
            }

            quiz.timerDuration -= Date.now() - startTimeData.startTimestamp;

            if (quiz.timerDuration <= 0) {
                return serializedErrorResponse("quiz-time-up", "Quiz time is up.");
            }
        }

        return serializedSuccessResponse(quiz);
    } catch (error) {
        console.error("An error occurred while fetching the quiz.", error);
        return serializedExceptionResponse(error);
    }
});

export const submitQuiz = functions.https.onCall(async (data, context) => {
    const { quizId, answerList } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    const uid = context.auth.uid;

    if (!quizId || !Array.isArray(answerList)) {
        return serializedErrorResponse("invalid-argument", "The function must be called with a valid quizId and answerList.");
    }

    try {
        const quizDoc = await db.collection("quizzes").doc(quizId).get();

        if (!quizDoc.exists) {
            return serializedErrorResponse("quiz-not-found", "Quiz not found.");
        }

        const quizData = quizDoc.data();

        if (!quizData || !quizData.isOpen) {
            return serializedErrorResponse("quiz-not-open", "Quiz is not open.");
        }

        const answerDoc = await db
            .collection("users")
            .doc(uid)
            .collection("quizResults")
            .doc(quizId)
            .get();

        if (answerDoc.exists) {
            return serializedErrorResponse("quiz-already-submitted", "Quiz already submitted.");
        }

        let score = 0;
        const maxScore = quizData.maxScore;

        if (answerList.length !== quizData.questionList.length) {
            return serializedErrorResponse("invalid-argument", "The answerList must have the same length as the questionList.");
        }

        const questionListResponse: GenericResponse<Question[]> = await parseQuestionListRef(
            quizData.questionList,
            false
        );

        if (questionListResponse.error) {
            return serializedErrorResponse(questionListResponse.error.errorCode, questionListResponse.error.details);
        }

        const questionList: Question[] = questionListResponse.data as Question[];

        questionList.forEach((question: Question, index: number) => {
            if (question.correctAnswer === answerList[index]) {
                score += question.value || 0;
            }
        });

        const startTimeDoc = await db
            .collection("users")
            .doc(uid)
            .collection("quizStartTimes")
            .doc(quizId)
            .get();

        if (!startTimeDoc.exists) {
            return serializedErrorResponse("quiz-start-time-not-found", "Quiz start time for user not found.");
        }

        const startTimeData = startTimeDoc.data();

        if (!startTimeData) {
            return serializedErrorResponse("quiz-start-time-not-found", "Quiz start time for user not found.");
        }

        if (
            startTimeData.startTimestamp + quizData.timerDuration + backoffTime <
            Date.now()
        ) {
            return serializedErrorResponse("quiz-time-up", "Quiz time is up.");
        }

        const quizTitle: string = quizData.title;

        const result: QuizResult = { score, maxScore, quizTitle: quizTitle };

        await db
            .collection("users")
            .doc(uid)
            .collection("quizResults")
            .doc(quizId)
            .set(result);

        const userDoc = await db.collection("users").doc(uid).get();
        const userData = userDoc.data();
        if (!userData) {
            return serializedErrorResponse("user-not-found", "User data not found.");
        }

        const group = (await parseGroupRef(userData.group)).data;
        if (!group) {
            return serializedErrorResponse("group-not-found", "Group data not found.");
        }

        // Update realtime database
        await admin.database()
            .ref(`leaderboard/users/${uid}`)
            .transaction((currentUser) => {
                return {
                    ...currentUser,
                    score: (currentUser?.score || 0) + score,
                    timestamp: Date.now(),
                };
            })
        await admin.database()
            .ref(`leaderboard/groups/${group.groupId}`)
            .transaction((currentGroup) => {
                return {
                    ...currentGroup,
                    score: (currentGroup?.score || 0) + score,
                    timestamp: Date.now(),
                };
            })

        return serializedSuccessResponse(result);
    } catch (error) {
        console.error("An error occurred while submitting the quiz.", error);
        return serializedExceptionResponse(error);
    }
});

export const getQuizHistory = functions.https.onCall(async (_, context) => {
    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
        const quizResultsSnapshot = await db
            .collection("users")
            .doc(context.auth.uid)
            .collection("quizResults")
            .get();

        if (!quizResultsSnapshot) {
            return serializedErrorResponse("quiz-results-not-found", "Quiz results not found.");
        }

        const quizResults = await Promise.all(
            quizResultsSnapshot.docs.map(async (quizResultDoc) => {
                const quizResultData = quizResultDoc.data();

                const quizResult: QuizResult = {
                    quizTitle: quizResultData.quizTitle,
                    score: quizResultData.score,
                    maxScore: quizResultData.maxScore,
                };

                return quizResult;
            })
        );

        return serializedSuccessResponse(quizResults);
    } catch (error) {
        console.error("An error occurred while fetching the quiz history.", error);
        return serializedExceptionResponse(error);
    }
});

export const deleteQuiz = functions.https.onCall(async (data, context) => {
    const { quizId } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
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

        const quizRef = db.collection("quizzes").doc(quizId);
        const quizDoc = await quizRef.get();

        if (!quizDoc.exists) {
            return serializedErrorResponse("quiz-not-found", "Quiz not found.");
        }

        await quizRef.delete();

        return serializedSuccessResponse({ questionId: quizDoc.id });
    } catch (error) {
        console.error("An error occurred while deleting the quiz.", error);
        return serializedExceptionResponse(error);
    }
});

export const getQuizList = functions.https.onCall(async (_, context) => {
    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
        const userDoc = await db.collection("users").doc(context.auth.uid).get();

        if (!userDoc.exists) {
            return serializedErrorResponse("user-not-found", "User not found.");
        }

        const userData = userDoc.data();

        if (!userData) {
            return serializedErrorResponse("user-not-found", "User data not found.");
        }

        let quizQuery;
        if (userData.role === "staff") {
            quizQuery = db.collection("quizzes");
        } else {
            return serializedErrorResponse("permission-denied", "User not authorized to view quizzes.");
        };

        const quizSnapshot = await quizQuery.get();

        if (quizSnapshot.empty) {
            return serializedErrorResponse("quiz-list-not-found", "Quiz list not found.");
        }

        const quizList = await Promise.all(
            quizSnapshot.docs.map(async (quizDoc) => {
                const quizData = quizDoc.data();

                const questionListResponse: GenericResponse<Question[]> = await parseQuestionListRef(
                    quizData.questionList,
                    false
                );

                if (questionListResponse.error) {
                    return serializedErrorResponse(questionListResponse.error.errorCode, questionListResponse.error.details);
                }

                const questionList: Question[] = questionListResponse.data as Question[];

                const quiz: Quiz = {
                    quizId: quizDoc.id,
                    title: quizData.title,
                    creatorUid: quizData.creatorUid,
                    type: quizData.type,
                    talkId: quizData.talkId,
                    sponsorId: quizData.sponsorId,
                    maxScore: quizData.maxScore,
                    isOpen: quizData.isOpen,
                    questionList: questionList,
                    timerDuration: quizData.timerDuration,
                };

                return quiz;
            })
        );

        return serializedSuccessResponse(quizList);
    } catch (error) {
        console.error("An error occurred while fetching the quiz list.", error);
        return serializedExceptionResponse(error);
    }
});


export const addPointsToUsers = functions.https.onCall(async (data, context) => {
    const { title, value, userIdList } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
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

        let valueNum = parseFloat(value);

        const quizRef = db.collection("quizzes");
        const quizDoc = await quizRef.add({
            questionList: [],
            type: "custom",
            talkId: "",
            sponsorId: "",
            title: title,
            maxScore: valueNum,
            isOpen: false,
            timerDuration: 0,
            creatorUid: context.auth.uid,
        });

        const quizId = quizDoc.id;

        const batch = db.batch();

        userIdList.forEach((userId: string) => {
            const result: QuizResult = { score: valueNum, maxScore: valueNum, quizTitle: title };
            const userQuizResultRef = db.collection("users").doc(userId).collection("quizResults").doc(quizId);
            batch.set(userQuizResultRef, result);
        });

        await batch.commit();

        // Update realtime database
        await Promise.all(userIdList.map(async (userId: string) => {
            const userDoc = await db.collection("users").doc(userId).get();
            const userData = userDoc.data();

            if (!userData) {
                return serializedErrorResponse("user-not-found", "User data not found.");
            }

            const group = (await parseGroupRef(userData.group)).data;
            if (!group) {
                return serializedErrorResponse("group-not-found", "Group data not found.");
            }


            await admin.database()
                .ref(`leaderboard/users/${userId}`)
                .transaction((currentUser) => {
                    return {
                        ...currentUser,
                        score: (currentUser?.score || 0) + valueNum,
                        timestamp: Date.now(),
                    };
                });
            await admin.database()
                .ref(`leaderboard/groups/${group.groupId}`)
                .transaction((currentGroup) => {
                    return {
                        ...currentGroup,
                        score: (currentGroup?.score || 0) + valueNum,
                        timestamp: Date.now(),
                    };
                });

            return null;
        }));

        return serializedSuccessResponse({ quizId });
    } catch (error) {
        console.error("An error occurred while adding points to users.", error);
        return serializedExceptionResponse(error);
    }
});

export const toggleIsOpen = functions.https.onCall(async (data, context) => {
    const { quizId } = data;

    if (!context.auth) {
        return serializedErrorResponse("unauthenticated", "User must be authenticated.");
    }

    try {
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

        const quizRef = db.collection("quizzes").doc(quizId);
        const quizDoc = await quizRef.get();

        if (!quizDoc.exists) {
            return serializedErrorResponse("quiz-not-found", "Quiz not found.");
        }

        const quizData = quizDoc.data();

        if (!quizData) {
            return serializedErrorResponse("quiz-data-not-found", "Quiz data not found.");
        }

        const newIsOpen = !quizData.isOpen;
        await quizRef.update({ isOpen: newIsOpen });

        return serializedSuccessResponse({ quizId, isOpen: newIsOpen });
    } catch (error) {
        console.error("An error occurred while toggling the quiz open state.", error);
        return serializedExceptionResponse(error);
    }
});