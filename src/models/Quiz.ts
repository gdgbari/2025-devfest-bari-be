import { Question } from "@modelsQuestion";

export interface Quiz {
    quizId: string;
    title: string | null;
    type: string;
    talkId: string | null;
    sponsorId: string | null;
    maxScore: number | null;
    isOpen: boolean | null;
    questionList: Question[];
    timerDuration: number;
    creatorUid: string | null;
}